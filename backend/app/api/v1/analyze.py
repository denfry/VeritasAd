from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import Any, Dict, Optional
from pathlib import Path
import uuid
import shutil
import socket
import ipaddress
from urllib.parse import urlparse
import logging
from yt_dlp import YoutubeDL
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.disclosure_detector import DisclosureDetector
from app.services.link_detector import LinkDetector
from app.core.dependencies import get_current_user, increment_usage
from app.core.config import settings
from app.core.redis import get_redis, RedisClient
from app.core.errors import ValidationException, VideoProcessingException
from app.models.database import Analysis, AnalysisStatus, SourceType, get_db, User
from app.tasks.video_analysis import analyze_video_task
from app.utils.ad_classification import classify_advertising

logger = logging.getLogger(__name__)

# Allowed MIME types for video uploads
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-msvideo",  # .avi
    "video/quicktime",  # .mov
    "video/x-matroska",  # .mkv
    "video/webm",
    "video/x-flv",  # .flv
    "video/3gpp",  # .3gp
    "video/x-m4v",  # .m4v
}

router = APIRouter()
post_disclosure_detector = DisclosureDetector(use_llm=settings.USE_LLM)


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe to access (not internal/private/reserved).
    Prevents SSRF attacks by blocking access to:
    - Private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
    - Loopback (127.x.x.x, ::1)
    - Link-local (169.254.x.x)
    - localhost
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is safe, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme - only allow http/https
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Block localhost variations
        hostname_lower = hostname.lower()
        if hostname_lower in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return False
        
        # Resolve hostname and check all resolved IPs
        try:
            # Get all IP addresses for the hostname
            addr_infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
            for family, _, _, _, sockaddr in addr_infos:
                ip = sockaddr[0]
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    # Block private, reserved, loopback, and link-local IPs
                    if (ip_obj.is_private or 
                        ip_obj.is_reserved or 
                        ip_obj.is_loopback or 
                        ip_obj.is_link_local or
                        ip_obj.is_multicast):
                        return False
                except ValueError:
                    continue
            
            # Also check IPv6 if available
            addr_infos_v6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)
            for family, _, _, _, sockaddr in addr_infos_v6:
                ip = sockaddr[0]
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if (ip_obj.is_private or 
                        ip_obj.is_reserved or 
                        ip_obj.is_loopback or 
                        ip_obj.is_link_local or
                        ip_obj.is_multicast):
                        return False
                except ValueError:
                    continue
                    
        except socket.gaierror:
            # DNS resolution failed
            return False
        
        return True
    except Exception:
        return False


def _has_video_payload(info: Dict[str, Any]) -> bool:
    duration = info.get("duration")
    if isinstance(duration, (int, float)) and duration > 0:
        return True
    if info.get("width") or info.get("height"):
        return True
    formats = info.get("formats") or []
    for fmt in formats:
        vcodec = fmt.get("vcodec")
        if vcodec and vcodec != "none":
            return True
    return False


def _build_post_response(url: str, info: Dict[str, Any], source_type: SourceType) -> Dict[str, Any]:
    description = info.get("description", "") or ""
    title = info.get("title")
    uploader = info.get("uploader")
    view_count = info.get("view_count")
    
    # Run disclosure detection
    disclosure = post_disclosure_detector.analyze(text=description, description=title or "")
    disclosure_markers = disclosure.get("markers", [])
    cta_matches = disclosure.get("cta_matches", [])
    has_disclosure = disclosure.get("has_disclosure", False) or bool(disclosure_markers)
    has_cta = disclosure.get("has_cta", False)
    
    # Run link detection
    link_detector = LinkDetector()
    link_result = link_detector.analyze(text=description, description=title or "")
    has_commercial_links = link_result.get("has_ad_signals", False)
    commercial_urls = link_result.get("urls", [])
    link_score = link_result.get("score", 0.0)
    
    # Determine if advertising
    has_advertising = has_disclosure or has_cta or has_commercial_links
    confidence_score = max(disclosure.get("score", 0.0), link_score)
    
    # Classify
    classification = classify_advertising(
        has_advertising=has_advertising,
        disclosure_markers=disclosure_markers,
        detected_brands=[],
        detected_keywords=[],
        has_cta=has_cta,
        has_commercial_links=has_commercial_links,
        commercial_urls=commercial_urls,
    )

    return {
        "analysis_type": "post",
        "status": "completed",
        "video_id": info.get("id") or "post",
        "url": url,
        "source_type": source_type.value,
        "title": title,
        "uploader": uploader,
        "view_count": view_count,
        "has_advertising": has_advertising,
        "confidence_score": confidence_score,
        "disclosure_score": disclosure.get("score", 0.0),
        "link_score": link_score,
        "disclosure_markers": disclosure_markers,
        "cta_matches": cta_matches,
        "commercial_urls": commercial_urls,
        "disclosure_text": disclosure_markers,
        "ad_classification": classification["classification"],
        "ad_reason": classification["reason"],
        "detected_brands": [],
        "detected_keywords": [],
        "transcript": "",
    }


def _infer_source_type(url: Optional[str]) -> SourceType:
    if not url:
        return SourceType.FILE
    lowered = url.lower()
    if "youtu.be" in lowered or "youtube.com" in lowered:
        return SourceType.YOUTUBE
    if "t.me" in lowered or "telegram" in lowered:
        return SourceType.TELEGRAM
    if "instagram.com" in lowered or "instagr.am" in lowered:
        return SourceType.INSTAGRAM
    if "tiktok.com" in lowered:
        return SourceType.TIKTOK
    if "vk.com" in lowered or "vk.ru" in lowered:
        return SourceType.VK
    return SourceType.URL


@router.post("/check")
async def check_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
):
    if not file and not url:
        raise ValidationException("Provide a URL or upload a video file")

    source_type = _infer_source_type(url)

    if url and not file:
        # SSRF protection: Validate URL before processing
        if not is_safe_url(url):
            raise ValidationException("Invalid or unsafe URL")

        info: Optional[Dict[str, Any]] = None
        info_error: Optional[str] = None
        try:
            logger.info(f"Extracting video info from URL: {url}")
            with YoutubeDL(
                {
                    "skip_download": True,
                    "quiet": True,
                    "no_warnings": False,  # Enable warnings for debugging
                    "socket_timeout": settings.DOWNLOAD_SOCKET_TIMEOUT,
                    "retries": settings.DOWNLOAD_RETRIES,
                    "fragment_retries": settings.DOWNLOAD_FRAGMENT_RETRIES,
                    "noplaylist": True,
                    "js_runtimes": {"node": {}, "deno": {}},
                    "extract_flat": False,
                    "ignoreerrors": False,  # Don't ignore errors - we want to catch them
                }
            ) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info(f"Successfully extracted info: {info.get('title', 'Unknown') if info else 'No info'}")
        except Exception as exc:
            info_error = str(exc)
            logger.error(f"Failed to extract video info from {url}: {type(exc).__name__} - {info_error}")
            # Log full traceback for debugging
            logger.debug(f"Full exception details:", exc_info=True)

        if info and not _has_video_payload(info):
            logger.info(f"No video payload detected, treating as post analysis")
            await increment_usage(user, db)
            return _build_post_response(url, info, source_type)
        
        # If info extraction failed, return error early
        if info_error:
            logger.warning(f"Video info extraction failed, returning error to user")
            raise ValidationException(f"Failed to fetch video info: {info_error}")

    video_path: Optional[Path] = None
    source_url: Optional[str] = None

    if file:
        file_ext = Path(file.filename or "").suffix.lower()
        if file_ext and file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise ValidationException(
                f"Unsupported file extension: {file_ext}. "
                f"Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
            )

        # Validate MIME type if available
        if hasattr(file, 'content_type') and file.content_type:
            if file.content_type not in ALLOWED_MIME_TYPES:
                raise ValidationException(
                    f"Invalid content type: {file.content_type}. "
                    f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
                )

        file_size = getattr(file, "size", None)
        if file_size is None:
            try:
                current_pos = file.file.tell()
                file.file.seek(0, 2)
                file_size = file.file.tell()
                file.file.seek(current_pos)
            except Exception:
                file_size = None

        if file_size is not None and file_size > settings.MAX_FILE_SIZE:
            raise ValidationException(
                f"File is too large. Max allowed size is {settings.MAX_FILE_SIZE} bytes"
            )

        video_id = f"{uuid.uuid4().hex}"
        video_path = settings.upload_path / f"{video_id}.mp4"
        video_path.parent.mkdir(parents=True, exist_ok=True)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # For file uploads, video is already saved
        task_id = uuid.uuid4().hex
        analysis = Analysis(
            task_id=task_id,
            video_id=video_id,
            user_id=user.id,
            source_url=None,
            source_type=source_type,
            file_path=str(video_path),
            status=AnalysisStatus.QUEUED,
            progress=0,
        )
        db.add(analysis)
        await db.commit()

        await redis.set_task_progress(
            task_id, progress=0, status="queued", message="Queued for processing"
        )

        analyze_video_task.delay(
            task_id=task_id,
            video_path_param=str(video_path),
            source_url=None,
            source_type=source_type.value,
        )
    else:
        # For URL sources, pass URL to task for download with progress tracking
        source_url = url
        video_id = f"{uuid.uuid4().hex}"
        temp_video_path = settings.upload_path / f"{video_id}.mp4"

        task_id = uuid.uuid4().hex
        analysis = Analysis(
            task_id=task_id,
            video_id=video_id,
            user_id=user.id,
            source_url=source_url,
            source_type=source_type,
            file_path=str(temp_video_path),
            status=AnalysisStatus.QUEUED,
            progress=0,
        )
        db.add(analysis)
        await db.commit()

        await redis.set_task_progress(
            task_id, progress=0, status="queued", message="Queued for processing"
        )

        analyze_video_task.delay(
            task_id=task_id,
            video_path_param=str(temp_video_path),
            source_url=source_url,
            source_type=source_type.value,
        )

    await increment_usage(user, db)

    return {
        "analysis_type": "video",
        "status": "queued",
        "task_id": task_id,
        "video_id": video_id,
    }


@router.post("/post")
async def analyze_post(
    url: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # SSRF protection: Validate URL before processing
    if not is_safe_url(url):
        return {
            "analysis_type": "post",
            "status": "failed",
            "video_id": "post",
            "url": url,
            "error": "Invalid or unsafe URL",
        }
    
    try:
        with YoutubeDL({
            "skip_download": True,
            "quiet": True,
            "js_runtimes": {"node": {}, "deno": {}},
        }) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        return {
            "analysis_type": "post",
            "status": "failed",
            "video_id": "post",
            "url": url,
            "error": str(exc),
        }
    await increment_usage(user, db)
    return _build_post_response(url, info, _infer_source_type(url))
