from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Any, Dict
import asyncio
import json
from app.core.redis import get_redis, RedisClient
from app.core.dependencies import get_current_user
from app.core.errors import NotFoundException
from app.models.database import Analysis, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


def _serialize_analysis(analysis: Analysis) -> Dict[str, Any]:
    return {
        "analysis_type": "video",
        "task_id": analysis.task_id,
        "video_id": analysis.video_id,
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
        "disclosure_text": analysis.disclosure_markers or [],
        "ad_classification": analysis.ad_classification,
        "ad_reason": analysis.ad_reason,
        "duration": analysis.duration,
        "progress": analysis.progress,
        "error": analysis.error_message,
    }


async def progress_stream(
    task_id: str,
    redis: RedisClient,
) -> AsyncGenerator[str, None]:
    """
    Stream task progress updates via SSE

    Yields SSE formatted messages with progress updates
    """
    try:
        last_progress = -1
        max_iterations = 600  # 10 minutes max (600 * 1 second)
        iteration = 0

        while iteration < max_iterations:
            # Get current progress
            progress_data = await redis.get_task_progress(task_id)

            if not progress_data:
                payload = {"error": "Task not found"}
                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                break

            current_progress = progress_data.get("progress", 0)
            status = progress_data.get("status", "processing")
            message = progress_data.get("message", "")

            # Send update if progress changed
            if current_progress != last_progress:
                data = {
                    "task_id": task_id,
                    "progress": current_progress,
                    "status": status,
                    "message": message,
                }
                yield f"data: {json.dumps(data)}\n\n"
                last_progress = current_progress

            # Check if completed or failed
            if status in ["completed", "failed"]:
                logger.info("sse_stream_ended", task_id=task_id, status=status)
                break

            # Wait before next check
            await asyncio.sleep(1)
            iteration += 1

        # Send final message if timeout
        if iteration >= max_iterations:
            payload = {"error": "Stream timeout"}
            yield f"event: timeout\ndata: {json.dumps(payload)}\n\n"

    except Exception as e:
        logger.exception("sse_stream_error", task_id=task_id, error=str(e))
        payload = {"error": str(e)}
        yield f"event: error\ndata: {json.dumps(payload)}\n\n"


@router.get("/analysis/{task_id}/stream")
async def stream_analysis_progress(
    task_id: str,
    redis: RedisClient = Depends(get_redis),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream real-time progress updates for video analysis task

    Returns SSE (Server-Sent Events) stream with progress updates
    
    Security: Verifies task belongs to the authenticated user
    """
    # Check if task exists AND belongs to user (IDOR protection)
    result = await db.execute(
        select(Analysis).where(
            Analysis.task_id == task_id,
            Analysis.user_id == user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise NotFoundException(f"Task {task_id} not found")

    return StreamingResponse(
        progress_stream(task_id, redis),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/analysis/{task_id}/status")
async def get_analysis_status(
    task_id: str,
    redis: RedisClient = Depends(get_redis),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current status of analysis task (non-streaming)
    
    Security: Verifies task belongs to the authenticated user
    """
    # Check if task exists AND belongs to user (IDOR protection)
    result = await db.execute(
        select(Analysis).where(
            Analysis.task_id == task_id,
            Analysis.user_id == user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise NotFoundException(f"Task {task_id} not found")
    
    progress_data = await redis.get_task_progress(task_id)
    if not progress_data:
        raise NotFoundException(f"Task {task_id} not found")

    return progress_data


@router.get("/analysis/{task_id}/result")
async def get_analysis_result(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Get analysis result by task ID
    
    Security: Verifies task belongs to the authenticated user
    """
    result = await db.execute(
        select(Analysis).where(
            Analysis.task_id == task_id,
            Analysis.user_id == user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise NotFoundException(f"Task {task_id} not found")
    return _serialize_analysis(analysis)
