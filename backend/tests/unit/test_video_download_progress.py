import asyncio
import shutil
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.video_processor import VideoProcessor


def test_download_video_accepts_sync_progress_callback(monkeypatch):
    temp_dir = Path(__file__).resolve().parents[2] / ".test-temp" / uuid.uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=True)
    processor = VideoProcessor.__new__(VideoProcessor)
    processor.raw_dir = temp_dir

    progress_events = []

    def sync_progress(progress: int, message: str) -> None:
        progress_events.append((progress, message))

    monkeypatch.setattr(processor, "_build_auth_args", lambda url: [])
    generated_paths = []

    def fake_build_cmd(url, video_path, auth_args, **kwargs):
        generated_paths.append(video_path)
        return ["yt-dlp"]

    monkeypatch.setattr(processor, "_build_yt_dlp_download_cmd", fake_build_cmd)

    def fake_run(cmd, emit_progress):
        emit_progress(7, "Downloading video")
        generated_paths[-1].write_bytes(b"video")

        class Result:
            returncode = 0

        return Result(), []

    monkeypatch.setattr(processor, "_run_yt_dlp_with_progress", fake_run)

    try:
        downloaded_path = processor.download_video(
            "https://example.test/video.mp4",
            progress_callback=sync_progress,
        )

        assert downloaded_path is not None
        assert downloaded_path.exists()
        assert progress_events == [
            (5, "Downloading video"),
            (7, "Downloading video"),
            (15, "Processing video file"),
        ]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_build_auth_args_skips_browser_cookies_for_youtube(monkeypatch):
    processor = VideoProcessor.__new__(VideoProcessor)
    monkeypatch.setattr(
        "app.services.video_processor.settings",
        SimpleNamespace(
            YTDLP_COOKIES_FILE=None,
            YTDLP_COOKIES_FROM_BROWSER="chrome",
        ),
    )

    auth_args = processor._build_auth_args("https://www.youtube.com/watch?v=demo")
    assert auth_args == []


def test_download_video_reports_ffmpeg_hint(monkeypatch):
    temp_dir = Path(__file__).resolve().parents[2] / ".test-temp" / uuid.uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=True)
    processor = VideoProcessor.__new__(VideoProcessor)
    processor.raw_dir = temp_dir

    monkeypatch.setattr(processor, "_build_auth_args", lambda url: [])
    monkeypatch.setattr(processor, "_build_yt_dlp_download_cmd", lambda *args, **kwargs: ["yt-dlp"])

    class Result:
        returncode = 1

    monkeypatch.setattr(
        processor,
        "_run_yt_dlp_with_progress",
        lambda cmd, emit_progress: (
            Result(),
            ["ERROR: ffmpeg could not be found. Please install"],
        ),
    )

    with pytest.raises(RuntimeError, match="install ffmpeg"):
        processor.download_video("https://example.test/video.mp4")

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_threadsafe_progress_callback_uses_parent_loop():
    from app.tasks.video_analysis import _build_threadsafe_progress_callback

    parent_loop = asyncio.get_running_loop()
    progress_events = []

    async def update_progress(progress: int, message: str, stage: str = "download") -> None:
        progress_events.append(
            {
                "progress": progress,
                "message": message,
                "stage": stage,
                "loop": asyncio.get_running_loop(),
            }
        )

    progress_callback = _build_threadsafe_progress_callback(
        parent_loop,
        update_progress,
        task_id="task-1",
    )

    await asyncio.to_thread(progress_callback, 9, "Downloading video")

    assert progress_events == [
        {
            "progress": 9,
            "message": "Downloading video",
            "stage": "download",
            "loop": parent_loop,
        }
    ]
