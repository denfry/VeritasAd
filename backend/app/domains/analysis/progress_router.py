"""Analysis domain - progress streaming and results."""
from typing import Any, AsyncGenerator, Dict
import asyncio
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.redis import get_redis, RedisClient
from app.core.dependencies import get_current_user
from app.core.errors import NotFoundException
from app.models.database import Analysis, get_db, User
from app.domains.analysis.repository import AnalysisRepository
from app.domains.analysis.dependencies import get_analysis_repository

router = APIRouter()
logger = structlog.get_logger(__name__)


def _serialize_analysis(analysis: Analysis) -> Dict[str, Any]:
    """Serialize Analysis model to API response."""
    return {
        "analysis_type": "video",
        "task_id": analysis.task_id,
        "video_id": analysis.video_id,
        "status": (
            analysis.status.value if hasattr(analysis.status, "value") else analysis.status
        ),
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
    """Stream task progress updates via SSE."""
    try:
        last_progress = -1
        last_message = None
        last_status = None
        max_iterations = 600
        iteration = 0

        while iteration < max_iterations:
            progress_data = await redis.get_task_progress(task_id)

            if not progress_data:
                payload = {"error": "Task not found"}
                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                break

            current_progress = progress_data.get("progress", 0)
            status = progress_data.get("status", "processing")
            message = progress_data.get("message", "")
            stage = progress_data.get("stage")

            if current_progress != last_progress or status != last_status or message != last_message:
                data = {
                    "task_id": task_id,
                    "progress": current_progress,
                    "status": status,
                    "message": message,
                    "stage": stage,
                }
                yield f"data: {json.dumps(data)}\n\n"
                last_progress = current_progress
                last_status = status
                last_message = message

            if status in ["completed", "failed"]:
                logger.info("sse_stream_ended", task_id=task_id, status=status)
                break

            await asyncio.sleep(1)
            iteration += 1

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
):
    """Stream real-time progress updates for video analysis task."""
    task_data = await redis.get_task_progress(task_id)
    if not task_data:
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


@router.websocket("/analysis/{task_id}/ws")
async def stream_analysis_progress_ws(websocket: WebSocket, task_id: str):
    """WebSocket stream for real-time analysis progress."""
    await websocket.accept()
    redis = RedisClient()
    await redis.connect()
    try:
        last_progress = -1
        last_message = None
        last_status = None

        for _ in range(600):
            progress_data = await redis.get_task_progress(task_id)
            if not progress_data:
                await websocket.send_json({"error": "Task not found"})
                break

            current_progress = progress_data.get("progress", 0)
            status = progress_data.get("status", "processing")
            message = progress_data.get("message", "")
            stage = progress_data.get("stage")

            if current_progress != last_progress or status != last_status or message != last_message:
                await websocket.send_json(
                    {
                        "task_id": task_id,
                        "progress": current_progress,
                        "status": status,
                        "message": message,
                        "stage": stage,
                    }
                )
                last_progress = current_progress
                last_status = status
                last_message = message

            if status in ["completed", "failed"]:
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("ws_progress_client_disconnected", task_id=task_id)
    finally:
        await redis.close()


@router.get("/analysis/{task_id}/status")
async def get_analysis_status(
    task_id: str,
    redis: RedisClient = Depends(get_redis),
    user=Depends(get_current_user),
):
    """Get current status of analysis task (non-streaming)."""
    progress_data = await redis.get_task_progress(task_id)

    if not progress_data:
        raise NotFoundException(f"Task {task_id} not found")

    return progress_data


@router.get("/analysis/{task_id}/result")
async def get_analysis_result(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    repository: AnalysisRepository = Depends(get_analysis_repository),
):
    """Get analysis result by task ID."""
    analysis = await repository.get_by_task_id(db, task_id, user_id=user.id)
    if not analysis:
        raise NotFoundException(f"Task {task_id} not found")
    return _serialize_analysis(analysis)
