from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.dependencies import get_current_admin_user
from app.models.database import get_db, User, Analysis, AnalysisStatus, UserPlan, UserRole
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta

router = APIRouter()


class UserListItem(BaseModel):
    id: int
    email: Optional[str]
    supabase_user_id: Optional[str]
    plan: str
    role: str
    daily_limit: int
    daily_used: int
    total_analyses: int
    is_active: bool
    is_banned: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    role: Optional[str] = None
    plan: Optional[str] = None
    daily_limit: Optional[int] = None
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None


class AnalyticsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_analyses: int
    analyses_today: int
    avg_confidence_score: float
    failed_analyses: int
    top_users: List[dict]
    plan_distribution: List[dict]
    chart_data: List[dict]


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users (admin only).
    """
    result = await db.execute(
        select(User)
        .order_by(desc(User.created_at))
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserListItem)
async def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user details (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.patch("/users/{user_id}", response_model=UserListItem)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update fields
    if user_update.role is not None:
        if user_update.role not in [UserRole.USER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )
        user.role = user_update.role
    
    if user_update.plan is not None:
        if user_update.plan not in [UserPlan.FREE, UserPlan.PRO, UserPlan.ENTERPRISE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan",
            )
        user.plan = user_update.plan
    
    if user_update.daily_limit is not None:
        user.daily_limit = user_update.daily_limit
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    if user_update.is_banned is not None:
        user.is_banned = user_update.is_banned
    
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analytics data (admin only).
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Active users today (users who made at least one analysis today)
    active_users_result = await db.execute(
        select(func.count(func.distinct(Analysis.user_id)))
        .where(Analysis.created_at >= today_start)
    )
    active_users_today = active_users_result.scalar() or 0
    
    # Total analyses
    total_analyses_result = await db.execute(select(func.count(Analysis.id)))
    total_analyses = total_analyses_result.scalar() or 0
    
    # Analyses today
    analyses_today_result = await db.execute(
        select(func.count(Analysis.id))
        .where(Analysis.created_at >= today_start)
    )
    analyses_today = analyses_today_result.scalar() or 0
    
    # Average confidence score
    avg_confidence_result = await db.execute(
        select(func.avg(Analysis.confidence_score))
        .where(Analysis.status == AnalysisStatus.COMPLETED)
    )
    avg_confidence = avg_confidence_result.scalar() or 0.0
    
    # Failed analyses
    failed_analyses_result = await db.execute(
        select(func.count(Analysis.id))
        .where(Analysis.status == AnalysisStatus.FAILED)
    )
    failed_analyses = failed_analyses_result.scalar() or 0
    
    # Top users by total analyses
    top_users_result = await db.execute(
        select(
            User.id,
            User.email,
            User.plan,
            User.total_analyses,
        )
        .order_by(desc(User.total_analyses))
        .limit(10)
    )
    top_users = [
        {
            "id": row.id,
            "email": row.email or "No email",
            "plan": row.plan,
            "total_analyses": row.total_analyses,
        }
        for row in top_users_result.all()
    ]

    # Plan distribution
    plan_dist_result = await db.execute(
        select(User.plan, func.count(User.id))
        .group_by(User.plan)
    )
    plan_distribution = [
        {"name": row[0].capitalize(), "value": row[1]}
        for row in plan_dist_result.all()
    ]

    # Chart data (last 24 hours)
    chart_data = []
    for i in range(24):
        hour_ago = now - timedelta(hours=24-i)
        hour_ago_end = hour_ago + timedelta(hours=1)
        
        # Count analyses in this hour
        analyses_count_result = await db.execute(
            select(func.count(Analysis.id))
            .where(Analysis.created_at >= hour_ago)
            .where(Analysis.created_at < hour_ago_end)
        )
        analyses_count = analyses_count_result.scalar() or 0
        
        # Average latency for completed analyses in this hour
        # (completed_at - created_at)
        latency_result = await db.execute(
            select(func.avg(Analysis.completed_at - Analysis.created_at))
            .where(Analysis.created_at >= hour_ago)
            .where(Analysis.created_at < hour_ago_end)
            .where(Analysis.status == AnalysisStatus.COMPLETED)
            .where(Analysis.completed_at.is_not(None))
        )
        avg_latency_td = latency_result.scalar()
        avg_latency_ms = 0
        if avg_latency_td:
            avg_latency_ms = int(avg_latency_td.total_seconds() * 1000)
        
        # System load mock - based on analyses count
        load = min(100, (analyses_count / 10) * 100) if analyses_count > 0 else 0
        
        chart_data.append({
            "time": hour_ago.strftime("%H:%M"),
            "analyses": analyses_count,
            "latency": avg_latency_ms or 120, # Default mock latency if no data
            "load": load or 5 # Default mock load
        })
    
    return AnalyticsResponse(
        total_users=total_users,
        active_users_today=active_users_today,
        total_analyses=total_analyses,
        analyses_today=analyses_today,
        avg_confidence_score=round(float(avg_confidence), 2),
        failed_analyses=failed_analyses,
        top_users=top_users,
        plan_distribution=plan_distribution,
        chart_data=chart_data,
    )
