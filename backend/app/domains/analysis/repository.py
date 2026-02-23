"""Analysis domain repository - data access layer."""
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Analysis, AnalysisStatus, SourceType, User


class AnalysisRepository:
    """Repository for Analysis model CRUD operations."""

    async def create(
        self,
        session: AsyncSession,
        *,
        task_id: str,
        video_id: str,
        user_id: int,
        source_url: Optional[str] = None,
        source_type: SourceType,
        file_path: Optional[str] = None,
    ) -> Analysis:
        """Create a new analysis record."""
        analysis = Analysis(
            task_id=task_id,
            video_id=video_id,
            user_id=user_id,
            source_url=source_url,
            source_type=source_type,
            file_path=file_path,
            status=AnalysisStatus.QUEUED,
            progress=0,
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        return analysis

    async def get_by_task_id(
        self,
        session: AsyncSession,
        task_id: str,
        user_id: Optional[int] = None,
    ) -> Optional[Analysis]:
        """Get analysis by task_id, optionally scoped to user."""
        query = select(Analysis).where(Analysis.task_id == task_id)
        if user_id is not None:
            query = query.where(Analysis.user_id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_analyses(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Analysis]:
        """Get user's analysis history, ordered by created_at descending."""
        query = (
            select(Analysis)
            .where(Analysis.user_id == user_id)
            .order_by(desc(Analysis.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_user_analyses_count(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:
        """Get total count of user's analyses."""
        query = select(Analysis).where(Analysis.user_id == user_id)
        result = await session.execute(query)
        return len(list(result.scalars().all()))
