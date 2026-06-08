"""Upload domain - video upload for annotation dataset."""
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import uuid
import structlog

from fastapi import APIRouter, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi import UploadFile

from app.core.config import settings
from app.core.dependencies import get_api_key

router = APIRouter()
logger = structlog.get_logger(__name__)

RAW_DIR = settings.data_path / "raw"
RAW_DIR.mkdir(exist_ok=True, parents=True)


@router.post("")  # alias for POST /api/v1/upload (thesis app. B)
@router.post("/video")
async def upload_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    api_key: str = Depends(get_api_key),
):
    """Upload video for annotation (file or URL download)."""
    if not file and not url:
        raise HTTPException(400, "Provide file or URL")

    video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    video_path = RAW_DIR / f"{video_id}.mp4"

    try:
        if file:
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source = "file"
        else:
            cmd = [
                "yt-dlp", "-o", str(video_path), "--retries", "3",
                "--quiet", "--no-warnings",
                url
            ]
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if result.returncode != 0:
                raise HTTPException(400, f"yt-dlp error: {result.stderr}")
            source = "url"

        annotate_script = Path(__file__).resolve().parents[4] / "scripts" / "auto_annotate.py"
        if annotate_script.exists():
            annotate_cmd = [
                "python",
                str(annotate_script),
                "--video-path",
                str(video_path),
            ]
            annotate_result = subprocess.run(annotate_cmd, capture_output=True, text=True)
            if annotate_result.returncode != 0:
                logger.error(f"annotation_failed - stderr={annotate_result.stderr}")
                raise HTTPException(500, "Video processing failed")
        else:
            logger.warning("annotation_script_missing - skipping dataset annotation")

        return JSONResponse(
            {
                "status": "success",
                "video_id": video_id,
                "source": source,
                "message": "Video uploaded successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"upload_error - error={str(e)}")
        raise HTTPException(500, str(e))
