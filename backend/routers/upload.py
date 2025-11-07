from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import subprocess
import uuid
from datetime import datetime
import logging

# **Configure logging for debugging and monitoring**
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

# **Define directories for raw videos and annotated dataset**
RAW_DIR = Path("../data/raw")
ANNOTATED_DIR = Path("../data/annotated/disclosure_dataset")

# Ensure required directories exist
RAW_DIR.mkdir(exist_ok=True)
ANNOTATED_DIR.mkdir(exist_ok=True)


@router.post("/video")
async def upload_video(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    """
    Upload a video either via file upload or URL (supports YouTube, Telegram, etc.).
    Downloads (if URL), saves to raw storage, auto-annotates, and adds to dataset.

    Args:
        file: Optional uploaded video file
        url: Optional video URL to download

    Returns:
        JSONResponse with video_id, source, and processing status
    """
    # ! Validate input: Require at least one of file or URL
    if not file and not url:
        raise HTTPException(400, "Either file or URL must be provided")

    # Generate unique video ID using timestamp and random suffix
    video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    video_path = RAW_DIR / f"{video_id}.mp4"

    try:
        source = ""

        if file:
            # Save uploaded file directly to disk
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source = "file"
            logger.info(f"File uploaded successfully: {video_path}")

        else:
            # **Download video using yt-dlp with enhanced reliability**
            cmd = [
                "yt-dlp",
                "-o", str(video_path),
                "--no-warnings",           # Suppress non-critical warnings
                "--extractor-retries", "3" # Retry failed extractors up to 3 times
            ]

            # ? Consider fallback for non-Chrome browsers (e.g., Firefox)
            # ! Security note: Cookies from browser could expose user data—sanitize in prod
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]

            cmd.append(url)

            logger.info(f"Running yt-dlp command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Prevent hanging on slow downloads
            )

            # Log yt-dlp output for debugging
            logger.info(f"yt-dlp stdout: {result.stdout}")
            logger.info(f"yt-dlp stderr: {result.stderr}")

            # Check for download failures
            if result.returncode != 0:
                error_msg = f"Download failed: {result.stderr or 'Unknown error'} (code: {result.returncode})"
                logger.error(error_msg)
                raise HTTPException(400, error_msg)

            # Validate downloaded file exists and is not empty
            if not video_path.exists() or video_path.stat().st_size == 0:
                raise HTTPException(400, "Download completed but file is missing or empty")

            source = "url"
            logger.info(f"Video downloaded: {video_path} ({video_path.stat().st_size} bytes)")

        # **Run auto-annotation script on the saved video**
        # TODO: Add async support for long-running annotations to avoid blocking
        annotate_cmd = ["python", "../scripts/auto_annotate.py", "--video-path", str(video_path)]
        annotate_result = subprocess.run(annotate_cmd, capture_output=True, text=True)

        if annotate_result.returncode != 0:
            error_msg = f"Annotation failed: {annotate_result.stderr}"
            logger.error(error_msg)
            raise HTTPException(500, f"Video processing error: {annotate_result.stderr}")

        # Return success response with metadata
        return JSONResponse({
            "status": "success",
            "video_id": video_id,
            "source": source,
            "message": "Video processed and added to dataset",
            "file_size": video_path.stat().st_size if video_path.exists() else 0
        })

    except HTTPException:
        # Re-raise known HTTP errors (400/500 from yt-dlp or validation)
        raise
    except Exception as e:
        # Catch unexpected errors and log them
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(500, error_msg)

# FIXME: Add cleanup for failed uploads (e.g., delete partial files on error)
