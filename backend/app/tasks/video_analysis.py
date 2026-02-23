from celery import Task
from typing import Dict, Any
from datetime import datetime, timezone
import structlog
from pathlib import Path
import asyncio
from app.core.celery import celery_app
from app.core.redis import RedisClient
from app.core.config import settings
from app.services.video_processor import VideoProcessor
from app.services.link_detector import LinkDetector
from app.models.database import AsyncSessionLocal, Analysis, AnalysisStatus
from app.utils.ad_classification import classify_advertising
from sqlalchemy import select

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


@celery_app.task(base=CallbackTask, bind=True, name="analyze_video")
def analyze_video_task(
    self,
    task_id: str,
    video_path_param: str,
    source_url: str | None = None,
    source_type: str = "file",
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
        task_id_current = task_id  # Keep track of task_id for logging

        try:
            await task_redis.connect()

            # Update status to processing
            await task_redis.set_task_progress(
                task_id,
                progress=0,
                status="processing",
                message="Preparing analysis",
                stage="prepare",
            )

            async with AsyncSessionLocal() as db:
                # Get analysis record
                result = await db.execute(select(Analysis).where(Analysis.task_id == task_id))
                analysis = result.scalar_one_or_none()

                if not analysis:
                    raise ValueError(f"Analysis not found: {task_id}")

                # Update status
                analysis.status = AnalysisStatus.PROCESSING
                await db.commit()

                # Lock for database operations to prevent concurrent access
                db_lock = asyncio.Lock()

                # Progress callback
                async def update_progress(progress: int, message: str, stage: str = "processing"):
                    # Update Redis (fast, handles concurrency better)
                    await task_redis.set_task_progress(
                        task_id,
                        progress=progress,
                        status="processing",
                        message=message,
                        stage=stage,
                    )
                    
                    # Update DB with lock to prevent concurrent commit errors
                    try:
                        async with db_lock:
                            analysis.progress = progress
                            await db.commit()
                    except Exception as db_err:
                        # Log but don't fail the whole analysis if just a progress update failed
                        logger.warning("progress_db_update_failed", error=str(db_err), task_id=task_id)

                # Download video with progress tracking (for URL sources)
                if source_type != "file" and source_url:
                    # Download with progress tracking
                    await update_progress(0, "Uploading source", "upload")
                    downloaded_path = processor.download_video(
                        source_url,
                        progress_callback=update_progress
                    )
                    if downloaded_path:
                        video_path_current = str(downloaded_path)
                    else:
                        raise Exception(f"Video download returned no file for URL: {source_url}")

                # Run video processing
                await update_progress(25, "Analyzing video", "analyze")
                metadata = await processor.get_video_metadata(Path(video_path_current))
                async with db_lock:
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
                # analyze метод DisclosureDetector - синхронный, выполняем в thread pool
                transcript = audio_result.get("transcript", "")
                
                # Get description from metadata for link/CTA detection
                description = metadata.get("description", "")
                
                # Run disclosure detection
                disclosure_result = await asyncio.to_thread(
                    processor.disclosure_detector.analyze,
                    text=transcript,
                    description=description
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
                cta_matches = disclosure_result.get("cta_matches", [])
                link_score = link_result.get("score", 0.0)

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
                async with db_lock:
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
                    analysis.erids = disclosure_result.get("erids", [])
                    analysis.promo_codes = disclosure_result.get("promo_codes", [])
                    analysis.ad_classification = classification["classification"]
                    analysis.ad_reason = classification["reason"]
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
                    "commercial_urls": link_result.get("urls", []),
                    "ad_classification": classification["classification"],
                    "ad_reason": classification["reason"],
                }
                
        except Exception as e:
            logger.exception("analysis_failed", task_id=task_id, error=str(e))
            
            # Update database
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Analysis).where(Analysis.task_id == task_id))
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error_message = str(e)
                    analysis.progress = 0
                    await db.commit()
            
            # Update Redis
            await task_redis.set_task_progress(
                task_id,
                progress=0,
                status="failed",
                message=str(e),
                stage="failed",
            )
            
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

    # Run async function using asyncio.run
    return asyncio.run(run_analysis())
