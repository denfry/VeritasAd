try:
    from celery import Task
    from celery.exceptions import SoftTimeLimitExceeded
except ImportError:  # pragma: no cover - optional dependency for worker runtime
    class Task:  # type: ignore[override]
        pass
    class SoftTimeLimitExceeded(Exception):  # type: ignore[override]
        pass
from typing import Dict, Any
from datetime import datetime, timezone
import structlog
from pathlib import Path
import asyncio
from app.core.celery import celery_app
from app.core.errors import ErrorCode
from app.core.redis import RedisClient
from app.core.config import settings
from app.services.video_processor import VideoProcessor
from app.services.link_detector import LinkDetector
from app.services.video_download_errors import classify_processing_error
from app.models.database import AsyncSessionLocal, Analysis, AnalysisStatus
from app.utils.ad_classification import classify_advertising
from sqlalchemy import select, update

logger = structlog.get_logger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for progress tracking"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logger.error(
            "task_failed",
            task_id=task_id,
            error=str(exc),
            traceback=str(einfo),
        )


async def _mark_task_failed(
    task_redis: RedisClient,
    task_id: str,
    error_info: Dict[str, str],
) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Analysis).where(Analysis.task_id == task_id))
        analysis = result.scalar_one_or_none()
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = error_info["user_message"]
            analysis.progress = 0
            await db.commit()

    await task_redis.set_task_progress(
        task_id,
        progress=0,
        status="failed",
        message=error_info["user_message"],
        stage="failed",
        error_code=error_info["error_code"],
    )


def _dispose_db_connections() -> None:
    # Dispose old engine connections before creating a new event loop.
    from app.models.database import engine as _db_engine

    _db_engine.sync_engine.dispose(close=False)


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="download_video",
    soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    time_limit=settings.CELERY_TASK_TIME_LIMIT,
)
def download_video_task(
    self,
    task_id: str,
    video_path_param: str,
    source_url: str,
    source_type: str = "url",
) -> Dict[str, Any]:
    """Download a remote source to disk, then enqueue analysis."""

    async def run_download():
        processor = VideoProcessor()
        task_redis = RedisClient()
        video_path_current = video_path_param
        download_succeeded = False

        try:
            await task_redis.connect()

            await task_redis.set_task_progress(
                task_id,
                progress=0,
                status="processing",
                message="Preparing download",
                stage="download_prepare",
            )

            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Analysis).where(Analysis.task_id == task_id))
                analysis = result.scalar_one_or_none()
                if not analysis:
                    raise ValueError(f"Analysis not found: {task_id}")

                analysis.status = AnalysisStatus.PROCESSING
                await db.commit()

            progress_lock = asyncio.Lock()
            last_reported_progress = 0

            async def persist_progress(progress: int) -> None:
                async with AsyncSessionLocal() as progress_db:
                    await progress_db.execute(
                        update(Analysis)
                        .where(Analysis.task_id == task_id)
                        .values(progress=progress)
                    )
                    await progress_db.commit()

            async def update_progress(progress: int, message: str, stage: str = "download"):
                nonlocal last_reported_progress

                async with progress_lock:
                    if progress <= last_reported_progress:
                        return
                    last_reported_progress = progress

                await task_redis.set_task_progress(
                    task_id,
                    progress=progress,
                    status="processing",
                    message=message,
                    stage=stage,
                )

                try:
                    await persist_progress(progress)
                except Exception as db_err:
                    logger.warning(
                        "download_progress_db_update_failed",
                        error=str(db_err),
                        task_id=task_id,
                    )

            await update_progress(5, "Downloading source video", "download")
            downloaded_path = await asyncio.to_thread(
                processor.download_video,
                source_url,
                progress_callback=update_progress,
            )
            if not downloaded_path:
                raise RuntimeError(f"Video download returned no file for URL: {source_url}")

            video_path_current = str(downloaded_path)

            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Analysis).where(Analysis.task_id == task_id))
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.file_path = video_path_current
                    analysis.progress = max(analysis.progress or 0, 20)
                    await db.commit()

            await task_redis.set_task_progress(
                task_id,
                progress=20,
                status="processing",
                message="Download complete, queuing analysis",
                stage="download_complete",
            )

            analyze_video_task.apply_async(
                kwargs={
                    "task_id": task_id,
                    "video_path_param": video_path_current,
                    "source_url": source_url,
                    "source_type": source_type,
                    "initial_progress": 20,
                },
                queue="analysis",
            )

            logger.info(
                "download_completed",
                task_id=task_id,
                source_url=source_url,
                video_path=video_path_current,
            )
            download_succeeded = True

            return {
                "task_id": task_id,
                "status": "queued_for_analysis",
                "video_path": video_path_current,
            }

        except SoftTimeLimitExceeded as e:
            logger.warning("download_timed_out", task_id=task_id, error=str(e))
            error_info = {
                "error_code": ErrorCode.VIDEO_DOWNLOAD_FAILED,
                "user_message": "Video download timed out before completion. Please retry later or upload the file directly.",
            }
            await _mark_task_failed(task_redis, task_id, error_info)
            raise
        except Exception as e:
            logger.exception("download_failed", task_id=task_id, error=str(e))
            error_info = classify_processing_error(str(e))
            await _mark_task_failed(task_redis, task_id, error_info)
            raise
        finally:
            try:
                if not download_succeeded and video_path_current:
                    path_to_cleanup = Path(video_path_current)
                    if path_to_cleanup.exists():
                        path_to_cleanup.unlink()
                        logger.info(
                            "partial_download_cleaned",
                            task_id=task_id,
                            path=str(path_to_cleanup),
                        )
            except Exception as cleanup_error:
                logger.warning(
                    "download_cleanup_failed",
                    task_id=task_id,
                    path=video_path_current,
                    error=str(cleanup_error),
                )
            await task_redis.close()

    _dispose_db_connections()
    return asyncio.run(run_download())


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="analyze_video",
    soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    time_limit=settings.CELERY_TASK_TIME_LIMIT,
)
def analyze_video_task(
    self,
    task_id: str,
    video_path_param: str,
    source_url: str | None = None,
    source_type: str = "file",
    initial_progress: int = 0,
) -> Dict[str, Any]:
    """
    Background task for video analysis

    Args:
        task_id: Unique task identifier
        video_path_param: Path to video file
        source_url: Original video URL (if applicable)
        source_type: Source type (file, url, youtube, etc.)

    Returns:
        Analysis results dictionary
    """
    async def run_analysis():
        processor = VideoProcessor()
        task_redis = RedisClient()
        video_path_current = video_path_param  # Keep track of video path for cleanup

        try:
            await task_redis.connect()

            # Update status to processing
            await task_redis.set_task_progress(
                task_id,
                progress=max(initial_progress, 0),
                status="processing",
                message="Preparing analysis",
                stage="prepare",
            )

            async with AsyncSessionLocal() as db:
                from sqlalchemy.orm import joinedload
                # Get analysis record with user to check plan
                result = await db.execute(
                    select(Analysis)
                    .options(joinedload(Analysis.user))
                    .where(Analysis.task_id == task_id)
                )
                analysis = result.scalar_one_or_none()

                if not analysis:
                    raise ValueError(f"Analysis not found: {task_id}")

                user_plan = analysis.user.plan if analysis.user else "free"

                # Update status
                analysis.status = AnalysisStatus.PROCESSING
                analysis.progress = max(initial_progress, 0)
                await db.commit()

                # Progress updates use a dedicated session to avoid re-entrant commits
                # on the main analysis session while yt-dlp emits callback events.
                progress_lock = asyncio.Lock()
                last_reported_progress = 0

                async def persist_progress(progress: int) -> None:
                    async with AsyncSessionLocal() as progress_db:
                        await progress_db.execute(
                            update(Analysis)
                            .where(Analysis.task_id == task_id)
                            .values(progress=progress)
                        )
                        await progress_db.commit()

                # Progress callback
                async def update_progress(progress: int, message: str, stage: str = "processing"):
                    nonlocal last_reported_progress

                    async with progress_lock:
                        if progress <= last_reported_progress:
                            return
                        last_reported_progress = progress

                    # Update Redis (fast, handles concurrency better)
                    await task_redis.set_task_progress(
                        task_id,
                        progress=progress,
                        status="processing",
                        message=message,
                        stage=stage,
                    )

                    # Update DB in its own session so callback commits do not collide
                    # with the main analysis transaction.
                    try:
                        await persist_progress(progress)
                    except Exception as db_err:
                        # Log but don't fail the whole analysis if just a progress update failed
                        logger.warning("progress_db_update_failed", error=str(db_err), task_id=task_id)

                # Run video processing
                await update_progress(25, "Analyzing video", "analyze")
                metadata = await processor.get_video_metadata(Path(video_path_current))
                analysis.duration = metadata.get("duration")
                await db.commit()

                await update_progress(45, "Detecting brands", "brand_detection")
                # detect_logos - синхронный метод, выполняем в thread pool
                brand_detection_done = asyncio.Event()

                async def brand_progress_heartbeat():
                    progress_value = 45
                    while not brand_detection_done.is_set():
                        await asyncio.sleep(8)
                        if brand_detection_done.is_set():
                            break
                        progress_value = min(64, progress_value + 2)
                        await update_progress(
                            progress_value,
                            "Detecting brands (this may take a few minutes)",
                            "brand_detection",
                        )

                heartbeat_task = asyncio.create_task(brand_progress_heartbeat())
                try:
                    visual_result = await asyncio.wait_for(
                        asyncio.to_thread(processor.detect_logos, Path(video_path_current)),
                        timeout=settings.BRAND_DETECTION_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "brand_detection_timeout",
                        task_id=task_id,
                        timeout_seconds=settings.BRAND_DETECTION_TIMEOUT,
                    )
                    visual_result = {"score": 0.0, "detected_brands": [], "frame_count": 0}
                finally:
                    brand_detection_done.set()
                    await heartbeat_task

                await update_progress(65, "Analyzing audio track", "analyze")
                # analyze метод AudioAnalyzer - синхронный, выполняем в thread pool
                audio_result = await asyncio.to_thread(processor.audio_analyzer.analyze, Path(video_path_current))

                await update_progress(80, "Detecting disclosure and CTA", "analyze")
                # analyze метод DisclosureDetector - теперь асинхронный
                transcript = audio_result.get("transcript", "")
                
                # URL fetches happen in the download worker; analysis stays local.
                description = metadata.get("description", "")
                
                # Run disclosure detection
                disclosure_result = await processor.disclosure_detector.analyze(
                    text=transcript,
                    description=description,
                    plan=user_plan
                )
                
                # Run link detection for hidden advertising
                link_detector = LinkDetector()
                link_result = await asyncio.to_thread(
                    link_detector.analyze,
                    text=transcript,
                    description=description
                )

                await update_progress(95, "Generating report", "report")

                # Calculate scores
                visual_score = visual_result.get("score", 0.0)
                audio_score = audio_result.get("score", 0.0)
                text_score = audio_score
                disclosure_score = disclosure_result.get("score", 0.0)
                disclosure_markers = disclosure_result.get("markers", [])
                link_score = link_result.get("score", 0.0)
                cta_matches = list(
                    dict.fromkeys(
                        (disclosure_result.get("cta_matches", []) or [])
                        + (link_result.get("cta_matches", []) or [])
                    )
                )
                commercial_urls = link_result.get("urls", [])

                # Combine detected brands from visual, OCR, and context discovery
                all_detected_brands = visual_result.get("detected_brands", [])
                
                # Add contextually discovered brands (from text near erid/promo)
                discovered_brands = disclosure_result.get("discovered_brands", [])
                for db in discovered_brands:
                    # Only add if not already detected visually (avoid duplicates)
                    if not any(v.get("name", "").lower() == db["name"].lower() for v in all_detected_brands):
                        all_detected_brands.append({
                            "name": db["name"],
                            "confidence": db["confidence"],
                            "source": db["source"],
                            "is_discovered": True
                        })

                # Combined confidence score with link detection
                confidence_score = (
                    visual_score * 0.25 +
                    audio_score * 0.25 +
                    text_score * 0.15 +
                    disclosure_score * 0.2 +
                    link_score * 0.15
                )

                # Has advertising if any signal is strong
                has_disclosure = disclosure_result.get("has_disclosure", False) or bool(disclosure_markers)
                has_cta = disclosure_result.get("has_cta", False)
                has_link_signals = link_result.get("has_ad_signals", False)
                has_advertising = confidence_score > 0.4 or has_disclosure or has_cta or has_link_signals

                classification = classify_advertising(
                    has_advertising=has_advertising,
                    disclosure_markers=disclosure_markers,
                    detected_brands=all_detected_brands,
                    detected_keywords=audio_result.get("keywords", []),
                    has_cta=has_cta,
                    has_commercial_links=has_link_signals,
                    commercial_urls=link_result.get("urls", []),
                )

                # Update analysis record
                analysis.has_advertising = has_advertising
                analysis.confidence_score = confidence_score
                analysis.visual_score = visual_score
                analysis.audio_score = audio_score
                analysis.text_score = text_score
                analysis.disclosure_score = disclosure_score
                analysis.detected_brands = all_detected_brands
                analysis.detected_keywords = audio_result.get("keywords", [])
                analysis.transcript = audio_result.get("transcript", "")
                analysis.disclosure_markers = disclosure_markers
                analysis.link_score = link_score
                analysis.cta_matches = cta_matches
                analysis.commercial_urls = commercial_urls
                analysis.erids = disclosure_result.get("erids", [])
                analysis.promo_codes = disclosure_result.get("promo_codes", [])
                analysis.ad_classification = classification["classification"]
                analysis.ad_reason = disclosure_result.get("ad_reason") or classification["reason"]
                analysis.method = disclosure_result.get("method")
                analysis.status = AnalysisStatus.COMPLETED
                analysis.progress = 100
                analysis.completed_at = datetime.now(timezone.utc)

                await db.commit()
                
                # Update Redis
                await task_redis.set_task_progress(
                    task_id,
                    progress=100,
                    status="completed",
                    message="Analysis completed",
                    stage="complete",
                )
                
                logger.info(
                    "analysis_completed",
                    task_id=task_id,
                    has_advertising=has_advertising,
                    confidence=confidence_score,
                )
                
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "has_advertising": has_advertising,
                    "confidence_score": confidence_score,
                    "visual_score": visual_score,
                    "audio_score": audio_score,
                    "text_score": text_score,
                    "disclosure_score": disclosure_score,
                    "link_score": link_score,
                    "detected_brands": visual_result.get("detected_brands", []),
                    "detected_keywords": audio_result.get("keywords", []),
                    "transcript": audio_result.get("transcript", ""),
                    "disclosure_markers": disclosure_markers,
                    "cta_matches": cta_matches,
                    "commercial_urls": commercial_urls,
                    "ad_classification": classification["classification"],
                    "ad_reason": classification["reason"],
                }
                
        except SoftTimeLimitExceeded as e:
            logger.warning("analysis_timed_out", task_id=task_id, error=str(e))
            error_info = {
                "error_code": ErrorCode.PROCESSING_FAILED,
                "user_message": "Video analysis took too long and was stopped. Please retry later or use a shorter video.",
            }
            await _mark_task_failed(task_redis, task_id, error_info)
            raise
        except Exception as e:
            logger.exception("analysis_failed", task_id=task_id, error=str(e))
            error_info = classify_processing_error(str(e))
            await _mark_task_failed(task_redis, task_id, error_info)
            raise
        finally:
            try:
                if video_path_current:
                    path_to_cleanup = Path(video_path_current)
                    if path_to_cleanup.exists():
                        path_to_cleanup.unlink()
                        logger.info(f"video_file_cleaned - task_id={task_id}, path={path_to_cleanup}")
            except Exception as cleanup_error:
                logger.warning(
                    f"video_file_cleanup_failed - task_id={task_id}, path={video_path_current}, "
                    f"error={str(cleanup_error)}"
                )
            await task_redis.close()

    return asyncio.run(run_analysis())
