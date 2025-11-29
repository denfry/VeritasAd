from celery import Task
from typing import Dict, Any
import structlog
from pathlib import Path
from app.core.celery import celery_app
from app.core.redis import redis_client
from app.services.video_processor import VideoProcessor
from app.models.database import AsyncSessionLocal, Analysis, AnalysisStatus
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
    video_path: str,
    source_url: str = None,
    source_type: str = "file",
) -> Dict[str, Any]:
    """
    Background task for video analysis
    
    Args:
        task_id: Unique task identifier
        video_path: Path to video file
        source_url: Original video URL (if applicable)
        source_type: Source type (file, url, youtube, etc.)
    
    Returns:
        Analysis results dictionary
    """
    import asyncio
    
    async def run_analysis():
        processor = VideoProcessor()
        
        try:
            # Update status to processing
            await redis_client.set_task_progress(
                task_id, progress=0, status="processing", message="Starting analysis"
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
                
                # Progress callback
                async def update_progress(progress: int, message: str):
                    await redis_client.set_task_progress(
                        task_id, progress=progress, status="processing", message=message
                    )
                
                # Run video processing
                await update_progress(10, "Extracting metadata")
                metadata = await processor.get_video_metadata(Path(video_path))
                
                await update_progress(20, "Detecting logos")
                visual_result = await processor.detect_logos(Path(video_path))
                
                await update_progress(50, "Analyzing audio")
                audio_result = await processor.analyze_audio(Path(video_path))
                
                await update_progress(80, "Detecting disclosure markers")
                disclosure_result = await processor.detect_disclosure(
                    audio_result.get("transcript", "")
                )
                
                # Calculate scores
                visual_score = visual_result.get("score", 0.0)
                audio_score = audio_result.get("score", 0.0)
                text_score = audio_score
                disclosure_score = disclosure_result.get("score", 0.0)
                
                confidence_score = (
                    visual_score * 0.3 +
                    audio_score * 0.3 +
                    text_score * 0.2 +
                    disclosure_score * 0.2
                )
                
                has_advertising = confidence_score > 0.5
                
                # Update analysis record
                analysis.has_advertising = has_advertising
                analysis.confidence_score = confidence_score
                analysis.visual_score = visual_score
                analysis.audio_score = audio_score
                analysis.text_score = text_score
                analysis.disclosure_score = disclosure_score
                analysis.detected_brands = visual_result.get("detected_brands", [])
                analysis.detected_keywords = audio_result.get("keywords", [])
                analysis.transcript = audio_result.get("transcript", "")
                analysis.disclosure_markers = disclosure_result.get("markers", [])
                analysis.status = AnalysisStatus.COMPLETED
                analysis.progress = 100
                
                await db.commit()
                
                # Update Redis
                await redis_client.set_task_progress(
                    task_id, progress=100, status="completed", message="Analysis complete"
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
                    await db.commit()
            
            # Update Redis
            await redis_client.set_task_progress(
                task_id, progress=0, status="failed", message=str(e)
            )
            
            raise
    
    # Run async function
    return asyncio.run(run_analysis())
