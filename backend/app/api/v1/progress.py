from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
from app.core.redis import get_redis, RedisClient
from app.core.dependencies import get_current_user
from app.core.errors import NotFoundException
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


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
                yield f"event: error
data: {{"error": "Task not found"}}

"
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
                yield f"data: {json.dumps(data)}

"
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
            yield f"event: timeout
data: {{"error": "Stream timeout"}}

"
            
    except Exception as e:
        logger.exception("sse_stream_error", task_id=task_id, error=str(e))
        yield f"event: error
data: {{"error": "{str(e)}"}}

"


@router.get("/analysis/{task_id}/stream")
async def stream_analysis_progress(
    task_id: str,
    redis: RedisClient = Depends(get_redis),
    user = Depends(get_current_user),
):
    """
    Stream real-time progress updates for video analysis task
    
    Returns SSE (Server-Sent Events) stream with progress updates
    """
    # Check if task exists
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


@router.get("/analysis/{task_id}/status")
async def get_analysis_status(
    task_id: str,
    redis: RedisClient = Depends(get_redis),
    user = Depends(get_current_user),
):
    """
    Get current status of analysis task (non-streaming)
    """
    progress_data = await redis.get_task_progress(task_id)
    
    if not progress_data:
        raise NotFoundException(f"Task {task_id} not found")
    
    return progress_data
