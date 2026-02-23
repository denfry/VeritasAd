"""Analysis domain - video analysis endpoints."""
from fastapi import APIRouter, File, UploadFile, Form, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.core.dependencies import get_current_user, increment_usage
from app.core.redis import get_redis, RedisClient
from app.models.database import get_db, User
from app.domains.analysis.service import AnalysisService
from app.domains.analysis.dependencies import get_analysis_service

router = APIRouter()


@router.post("/check")
async def check_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Submit video for analysis (URL or file upload)."""
    return await service.start_video_analysis(
        url=url,
        file=file,
        user=user,
        session=db,
        redis=redis,
        increment_usage_fn=increment_usage,
    )


@router.post("/post")
async def analyze_post(
    url: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Analyze social post metadata (no video download)."""
    return await service.analyze_post_metadata(
        url=url,
        user=user,
        session=db,
        increment_usage_fn=increment_usage,
    )


@router.get("/history")
async def get_analysis_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[Any]:
    """Get user's analysis history."""
    return await service.get_user_analyses(
        user=user,
        session=db,
        limit=limit,
        offset=offset,
    )
