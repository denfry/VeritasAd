import json
import logging
import subprocess
import glob
from pathlib import Path
from typing import Optional

from celery import states
from faster_whisper import WhisperModel

from .celery_app import celery_app
from .database import session_scope
from .models import Job, JobStatus
from .settings import get_settings
from .utils.platform import detect_platform
from .storage import upload_file

logger = logging.getLogger(__name__)
settings = get_settings()

def _update_job(
    job_id: str,
    status: JobStatus,
    result_path: Optional[str] = None,
    result_url: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    with session_scope() as session:
        job = session.get(Job, job_id)
        if not job:
            logger.error("Job not found: %s", job_id)
            return
        job.status = status
        if result_path is not None:
            job.result_path = result_path
        if result_url is not None:
            job.result_url = result_url
        if error is not None:
            job.error_message = error
        session.add(job)


def _fetch_metadata_generic(url: str) -> dict:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        "--skip-download",
        "--retries",
        "3",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error: {result.stderr}")
    return json.loads(result.stdout)


def _download_media(url: str, dest_dir: Path, job_id: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    # Use template to keep original extension; we'll pick the first produced file
    output_template = str(dest_dir / f"{job_id}.%(ext)s")
    cmd = [
        "yt-dlp",
        "-o",
        output_template,
        "--no-playlist",
        "--retries",
        "3",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp download error: {result.stderr}")

    # Find downloaded file
    matches = glob.glob(str(dest_dir / f"{job_id}.*"))
    if not matches:
        raise RuntimeError("Download finished but file not found")
    return Path(matches[0])


def _extract_frames(media_path: Path, frames_dir: Path, max_frames: int = 10) -> list[str]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    # 1 fps, cap by vframes
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(media_path),
        "-vf",
        "fps=1",
        "-vframes",
        str(max_frames),
        str(frames_dir / "frame_%03d.jpg"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning("Frame extraction failed: %s", result.stderr)
        return []
    return sorted([str(p) for p in frames_dir.glob("frame_*.jpg")])


def _extract_audio(media_path: Path, audio_dir: Path, job_id: str) -> Optional[str]:
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_path = audio_dir / f"{job_id}.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(media_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning("Audio extraction failed: %s", result.stderr)
        return None
    if not audio_path.exists():
        return None
    return str(audio_path)


def _transcribe_audio(audio_path: Path) -> Optional[str]:
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), language="ru", beam_size=1)
        text = " ".join([seg.text for seg in segments]).strip()
        return text
    except Exception as exc:
        logger.warning("Transcription failed: %s", exc)
        return None


def _classify_text_disclosure(text: str) -> tuple[str, float, str]:
    keywords = [
        "реклама",
        "спонсор",
        "партнер",
        "партнёр",
        "ad",
        "sponsored",
        "promo",
        "промо",
        "при поддержке",
        "коллаборация",
    ]
    lower = text.lower()
    hits = [kw for kw in keywords if kw in lower]
    score = min(1.0, 0.2 + 0.1 * len(hits)) if hits else 0.15
    label = "ad" if hits else "non-ad"
    reason = f"keywords: {', '.join(hits)}" if hits else "keywords not found"
    return label, score, reason


@celery_app.task(bind=True, name="backend.tasks.process_job")
def process_job(self, job_id: str, url: Optional[str]) -> str:
    """Download/collect metadata per platform and store JSON."""
    logger.info("Start job %s", job_id)
    _update_job(job_id, JobStatus.PROCESSING)

    try:
        platform = detect_platform(url or "")
        base_dir = Path(settings.storage_dir)
        meta_dir = base_dir / "meta"
        media_dir = base_dir / "media"
        frames_root = base_dir / "frames"
        audio_dir = base_dir / "audio"
        meta_dir.mkdir(parents=True, exist_ok=True)
        media_dir.mkdir(parents=True, exist_ok=True)
        frames_root.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)

        meta_path = meta_dir / f"{job_id}.json"

        # 1) Collect metadata
        metadata = _fetch_metadata_generic(url or "")
        metadata["platform"] = platform
        metadata["source_url"] = url

        # 2) Download media
        media_path = _download_media(url or "", media_dir, job_id)
        metadata["media_path"] = str(media_path)

        # 3) Extract frames
        frames_dir = frames_root / job_id
        frames = _extract_frames(media_path, frames_dir, max_frames=10)
        metadata["frames"] = frames

        # 4) Extract audio (16k mono wav) + transcription + heuristic classification
        audio_path = _extract_audio(media_path, audio_dir, job_id)
        if audio_path:
            metadata["audio_path"] = audio_path
            transcript = _transcribe_audio(Path(audio_path))
            if transcript:
                metadata["transcript"] = transcript
                label, score, reason = _classify_text_disclosure(transcript)
                metadata["analysis"] = {"label": label, "score": score, "reason": reason}

        # 5) Persist metadata
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        result_url = None
        media_url = None

        if settings.use_minio:
            # Upload files to MinIO
            media_url = upload_file(media_path, f"jobs/{job_id}/media/{media_path.name}")
            meta_url = upload_file(meta_path, f"jobs/{job_id}/meta/{meta_path.name}")
            result_url = meta_url
            # upload frames and audio best-effort
            for frame in frames:
                upload_file(Path(frame), f"jobs/{job_id}/frames/{Path(frame).name}")
            if audio_path:
                upload_file(Path(audio_path), f"jobs/{job_id}/audio/{Path(audio_path).name}")
            metadata["media_url"] = media_url
            metadata["result_url"] = result_url
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        _update_job(job_id, JobStatus.COMPLETED, result_path=str(meta_path), result_url=result_url)
        # also persist media_path/media_url
        with session_scope() as session:
            job = session.get(Job, job_id)
            if job:
                job.media_path = str(media_path)
                job.media_url = media_url
                session.add(job)
        return str(meta_path)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Job failed: %s", exc)
        _update_job(job_id, JobStatus.FAILED, error=str(exc))
        self.update_state(state=states.FAILURE, meta={"exc": str(exc)})
        raise

