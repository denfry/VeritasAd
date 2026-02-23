"""Analysis domain service - business logic layer."""
from typing import Any, Dict, Optional, List
from pathlib import Path
import uuid
import shutil
import logging
from fastapi import UploadFile
from yt_dlp import YoutubeDL

from app.core.config import settings
from app.core.errors import ValidationException
from app.core.redis import RedisClient
from app.models.database import Analysis, SourceType, User
from app.services.video_processor import VideoProcessor
from app.services.disclosure_detector import DisclosureDetector
from app.tasks.video_analysis import analyze_video_task
from app.utils.ad_classification import classify_advertising

from app.domains.analysis.repository import AnalysisRepository

logger = logging.getLogger(__name__)


def _has_video_payload(info: Dict[str, Any]) -> bool:
    """Check if metadata indicates video content."""
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


def _infer_source_type(url: Optional[str]) -> SourceType:
    """Infer source type from URL."""
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


class AnalysisService:
    """Service for video analysis business logic."""

    def __init__(
        self,
        repository: AnalysisRepository,
        processor: VideoProcessor,
        disclosure_detector: DisclosureDetector,
    ):
        self.repository = repository
        self.processor = processor
        self.disclosure_detector = disclosure_detector

    def _build_post_response(
        self, url: str, info: Dict[str, Any], source_type: SourceType
    ) -> Dict[str, Any]:
        """Build response for post-only analysis (no video)."""
        description = info.get("description", "") or ""
        title = info.get("title")
        uploader = info.get("uploader")
        view_count = info.get("view_count")
        disclosure = self.disclosure_detector.analyze(
            text=description, description=title or ""
        )
        disclosure_markers = disclosure.get("markers", [])
        has_disclosure = disclosure.get("has_disclosure", False) or bool(
            disclosure_markers
        )
        has_advertising = has_disclosure
        
        # Detect brands in text
        text_content = f"{title or ''} {description}".strip()
        detected_brands = self.processor.detect_brands_in_text(text_content)
        
        if detected_brands:
            has_advertising = True # If brands are detected, likely commercial
            
        classification = classify_advertising(
            has_advertising=has_advertising,
            disclosure_markers=disclosure_markers,
            detected_brands=detected_brands,
            detected_keywords=[],
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
            "confidence_score": disclosure.get("score", 0.0),
            "disclosure_score": disclosure.get("score", 0.0),
            "disclosure_markers": disclosure_markers,
            "disclosure_text": disclosure_markers,
            "ad_classification": classification["classification"],
            "ad_reason": classification["reason"],
            "detected_brands": detected_brands,
            "detected_keywords": [],
            "transcript": "",
        }

    async def start_video_analysis(
        self,
        *,
        url: Optional[str] = None,
        file: Optional[UploadFile] = None,
        user: User,
        session: Any,
        redis: RedisClient,
        increment_usage_fn: Any,
    ) -> Dict[str, Any]:
        """
        Start video analysis: validate input, create analysis record,
        queue Celery task, return task info.
        """
        if not file and not url:
            raise ValidationException("Provide a URL or upload a video file")

        source_type = _infer_source_type(url)
        logger.info(f"Starting video analysis: url={url[:50] if url else 'file'}, source_type={source_type}")

        if url and not file:
            info: Optional[Dict[str, Any]] = None
            info_error: Optional[str] = None
            try:
                logger.info(f"Extracting video info from URL: {url}")
                with YoutubeDL(
                    {
                        "skip_download": True,
                        "quiet": True,
                        "no_warnings": False,
                        "socket_timeout": settings.DOWNLOAD_SOCKET_TIMEOUT,
                        "retries": settings.DOWNLOAD_RETRIES,
                        "fragment_retries": settings.DOWNLOAD_FRAGMENT_RETRIES,
                        "noplaylist": True,
                        "js_runtimes": {"node": {}, "deno": {}},
                        "extract_flat": False,
                        "ignoreerrors": False,
                    }
                ) as ydl:
                    info = ydl.extract_info(url, download=False)
                    logger.info(f"Successfully extracted info: {info.get('title', 'Unknown') if info else 'No info'}")
            except Exception as exc:
                info_error = str(exc)
                logger.error(f"Failed to extract video info from {url}: {type(exc).__name__} - {info_error}")
                logger.debug(f"Full exception details:", exc_info=True)

            if info and not _has_video_payload(info):
                logger.info(f"No video payload detected, treating as post analysis")
                await increment_usage_fn(user, session)
                return self._build_post_response(url, info, source_type)
            
            # If info extraction failed, return error early
            if info_error:
                logger.warning(f"Video info extraction failed, returning error to user")
                raise ValidationException(f"Failed to fetch video info: {info_error}")

            source_url = url
            # Queue URL source and download inside background task.
            # This avoids request-time timeouts and improves YouTube reliability.
            video_id = f"{uuid.uuid4().hex}"
            video_path = None
            logger.info(f"Queuing URL analysis: video_id={video_id}, source_url={source_url[:50]}...")
        elif file:
            file_ext = Path(file.filename or "").suffix.lower()
            if file_ext and file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
                raise ValidationException(
                    f"Unsupported file extension: {file_ext}. "
                    f"Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
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
            logger.info(f"Saving uploaded file: {video_path} ({file_size} bytes)")
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source_url = None
            logger.info(f"Queuing file analysis: video_id={video_id}, path={video_path}")
        else:
            raise ValidationException("Provide a URL or upload a video file")

        task_id = uuid.uuid4().hex
        analysis = await self.repository.create(
            session,
            task_id=task_id,
            video_id=video_id,
            user_id=user.id,
            source_url=source_url,
            source_type=source_type,
            file_path=str(video_path) if video_path else None,
        )
        logger.info(f"Analysis record created: task_id={task_id}")

        await redis.set_task_progress(
            task_id, progress=0, status="queued", message="Queued for processing"
        )

        logger.info(f"Queuing Celery task: task_id={task_id}")
        analyze_video_task.delay(
            task_id=task_id,
            video_path_param=str(video_path) if video_path else "",
            source_url=source_url,
            source_type=source_type.value,
        )

        await increment_usage_fn(user, session)

        return {
            "analysis_type": "video",
            "status": "queued",
            "task_id": task_id,
            "video_id": video_id,
        }

    async def analyze_post_metadata(
        self,
        *,
        url: str,
        user: User,
        session: Any,
        increment_usage_fn: Any,
    ) -> Dict[str, Any]:
        """Analyze social post metadata without video download."""
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
        await increment_usage_fn(user, session)
        return self._build_post_response(url, info, _infer_source_type(url))

    async def get_user_analyses(
        self,
        *,
        user: User,
        session: Any,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get user's analysis history."""
        analyses = await self.repository.get_user_analyses(
            session, user_id=user.id, limit=limit, offset=offset
        )
        return [self._serialize_analysis(a) for a in analyses]

    async def get_user_analyses_count(
        self,
        *,
        user: User,
        session: Any,
    ) -> int:
        """Get total count of user's analyses."""
        return await self.repository.get_user_analyses_count(session, user_id=user.id)

    def _serialize_analysis(self, analysis: Analysis) -> Dict[str, Any]:
        """Serialize analysis model to dict."""
        return {
            "task_id": analysis.task_id,
            "video_id": analysis.video_id,
            "source_type": analysis.source_type.value if hasattr(analysis.source_type, "value") else analysis.source_type,
            "source_url": analysis.source_url,
            "status": analysis.status.value if hasattr(analysis.status, "value") else analysis.status,
            "has_advertising": analysis.has_advertising,
            "confidence_score": analysis.confidence_score,
            "visual_score": analysis.visual_score,
            "audio_score": analysis.audio_score,
            "text_score": analysis.text_score,
            "disclosure_score": analysis.disclosure_score,
            "detected_brands": analysis.detected_brands or [],
            "detected_keywords": analysis.detected_keywords or [],
            "transcript": analysis.transcript or "",
            "disclosure_markers": analysis.disclosure_markers or [],
            "ad_classification": analysis.ad_classification,
            "ad_reason": analysis.ad_reason,
            "duration": analysis.duration,
            "progress": analysis.progress,
            "error_message": analysis.error_message,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        }
