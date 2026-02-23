from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from datetime import datetime
import subprocess
import logging
from urllib.parse import urlparse

from app.core.dependencies import get_api_key
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

RAW_DIR = settings.data_path / "raw"
RAW_DIR.mkdir(exist_ok=True, parents=True)

# Whitelist разрешённых доменов для загрузки видео
ALLOWED_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "t.me",
    "telegram.org",
    "instagram.com",
    "instagr.am",
    "tiktok.com",
    "vk.com",
    "vk.ru",
}


def validate_url(url: str) -> bool:
    """
    Validate URL against whitelist of allowed domains.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid and from allowed domain
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Get and clean domain
        domain = parsed.netloc.lower()
        domain = domain.split(":")[0]  # Remove port if present
        
        # Check against whitelist
        return domain in ALLOWED_DOMAINS
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and command injection.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename with only safe characters
    """
    # Keep only alphanumeric, dots, underscores, and hyphens
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")
    return safe_name or "unnamed"


@router.post("/video")
async def upload_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    api_key: str = Depends(get_api_key)
):
    if not file and not url:
        raise HTTPException(400, "Нужен файл или URL")

    video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    video_path = RAW_DIR / f"{video_id}.mp4"

    try:
        if file:
            # Validate and sanitize filename
            if file.filename:
                safe_filename = sanitize_filename(file.filename)
                if not safe_filename:
                    raise HTTPException(400, "Invalid filename")
            
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source = "file"
        else:
            # Validate URL against whitelist
            if not validate_url(url):
                logger.warning(f"url_not_allowed - url={url[:100]}")
                raise HTTPException(400, "URL domain not allowed")

            cmd = [
                "yt-dlp", "-o", str(video_path), "--retries", "3",
                "--quiet", "--no-warnings",
                url
            ]
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90,
                check=False
            )
            if result.returncode != 0:
                logger.error(f"yt-dlp failed - stderr={result.stderr}")
                raise HTTPException(400, "Video download failed")
            source = "url"

        # Видео сохранено, готово для анализа через /api/v1/analyze/check
        return JSONResponse({
            "status": "success",
            "video_id": video_id,
            "source": source,
            "file_path": str(video_path),
            "message": "Видео загружено. Используйте /api/v1/analyze/check для анализа."
        })

    except subprocess.TimeoutExpired:
        logger.error("process_timeout")
        raise HTTPException(504, "Processing timeout")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"upload_error - error={str(e)}")
        raise HTTPException(500, str(e))
