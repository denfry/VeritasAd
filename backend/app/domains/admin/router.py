"""Admin domain router with BigTech-standard audit logging.

Features:
- Comprehensive audit logging for all actions
- Cursor-based pagination (like GitHub/Stripe API)
- Advanced filtering and sorting
- Bulk operations support
- Export capabilities
"""
from datetime import datetime, timezone
from typing import Optional, List, Literal
from pathlib import Path
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, or_
import structlog

from app.core.dependencies import get_current_admin_user
from app.models.database import (
    get_db,
    User,
    Analysis,
    AnalysisStatus,
    UserPlan,
    UserRole,
    AuditLog,
    AuditEventType,
)
from app.domains.admin.schemas import (
    UserListItem,
    UserUpdate,
    AnalyticsResponse,
    AuditLogListItem,
    UserListFilters,
    CursorPaginationResponse,
)
from app.services.audit_logger import AuditLogger, AuditEventType, log_admin_action

logger = structlog.get_logger(__name__)
router = APIRouter()


# ==================== USER MANAGEMENT ====================


@router.get("/users", response_model=CursorPaginationResponse[UserListItem])
async def list_users(
    request: Request,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    # Pagination
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination (base64 encoded user ID)"),
    # Sorting
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    # Filters
    search: Optional[str] = Query(None, description="Search by email or ID"),
    plan: Optional[str] = Query(None, description="Filter by plan"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_banned: Optional[bool] = Query(None, description="Filter by banned status"),
):
    """
    List users with advanced filtering, sorting, and cursor-based pagination.
    
    BigTech Standard API - similar to GitHub Users API, Stripe Customers API.
    
    Query Parameters:
    - **limit**: Number of results per page (1-100)
    - **cursor**: Pagination cursor (from previous response's next_cursor)
    - **sort_by**: Field to sort by (id, email, created_at, total_analyses)
    - **sort_order**: asc or desc
    - **search**: Search in email or ID
    - **plan**: Filter by plan (free, pro, enterprise)
    - **role**: Filter by role (user, admin)
    - **is_active**: Filter by active status
    - **is_banned**: Filter by banned status
    
    Returns:
    - **data**: List of users
    - **next_cursor**: Cursor for next page (null if last page)
    - **has_more**: Whether more results exist
    - **total_count**: Total matching results
    """
    # Build base query
    query = select(User)
    
    # Apply filters
    if search:
        # Search by email or ID
        if search.isdigit():
            query = query.where(or_(
                User.email.ilike(f"%{search}%"),
                User.id == int(search),
            ))
        else:
            query = query.where(User.email.ilike(f"%{search}%"))
    
    if plan:
        valid_plans = [p.value for p in UserPlan]
        if plan in valid_plans:
            query = query.where(User.plan == plan)
    
    if role:
        valid_roles = [r.value for r in UserRole]
        if role in valid_roles:
            query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_banned is not None:
        query = query.where(User.is_banned == is_banned)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0
    
    # Apply sorting
    valid_sort_fields = {
        "id": User.id,
        "email": User.email,
        "created_at": User.created_at,
        "total_analyses": User.total_analyses,
        "daily_used": User.daily_used,
    }
    
    sort_field = valid_sort_fields.get(sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Apply cursor-based pagination
    if cursor:
        import base64
        try:
            cursor_id = int(base64.b64decode(cursor).decode())
            # Get the value at the cursor position for proper pagination
            cursor_item = await db.get(User, cursor_id)
            if cursor_item:
                cursor_value = getattr(cursor_item, sort_by, cursor_item.created_at)
                if sort_order == "desc":
                    query = query.where(sort_field < cursor_value)
                else:
                    query = query.where(sort_field > cursor_value)
        except (ValueError, Exception):
            pass  # Invalid cursor, ignore
    
    # Apply limit (+1 to detect if there are more results)
    query = query.limit(limit + 1)
    
    # Execute query
    result = await db.execute(query)
    users = list(result.scalars().all())
    
    # Determine if there are more results
    has_more = len(users) > limit
    if has_more:
        users = users[:limit]  # Remove the extra item
    
    # Generate next cursor
    next_cursor = None
    if has_more and users:
        import base64
        next_cursor = base64.b64encode(str(users[-1].id).encode()).decode()
    
    # Log admin access to user list
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_USER_LIST,
        actor=admin,
        metadata={
            "limit": limit,
            "cursor": cursor,
            "filters": {
                "search": search,
                "plan": plan,
                "role": role,
                "is_active": is_active,
                "is_banned": is_banned,
            },
            "results_count": len(users),
        },
    )

    return CursorPaginationResponse(
        data=users,
        next_cursor=next_cursor,
        has_more=has_more,
        total_count=total_count,
    )


@router.get("/users/{user_id}", response_model=UserListItem)
async def get_user(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user details by ID (admin only).
    
    Logs audit trail for compliance.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        # Log failed access attempt
        audit_logger = AuditLogger(db, request)
        await audit_logger.log(
            event_type=AuditEventType.ADMIN_USER_VIEW,
            actor=admin,
            target_id=user_id,
            status="failure",
            error_message="User not found",
        )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Log admin access to user details
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_USER_VIEW,
        actor=admin,
        target_user=user,
    )

    return user


@router.patch("/users/{user_id}", response_model=UserListItem)
async def update_user(
    request: Request,
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user (admin only).

    All changes are logged to audit_logs for compliance.
    Sensitive changes (role, plan, ban status) are highlighted.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        audit_logger = AuditLogger(db, request)
        await audit_logger.log(
            event_type=AuditEventType.ADMIN_USER_UPDATE,
            actor=admin,
            target_id=user_id,
            status="failure",
            error_message="User not found",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Track changes for audit log
    changes = {}
    sensitive_changes = {}

    if user_update.role is not None and user_update.role != user.role:
        valid_roles = [e.value for e in UserRole]
        if user_update.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )
        changes["role"] = {"old": user.role, "new": user_update.role}
        sensitive_changes["role"] = changes["role"]
        user.role = user_update.role

    if user_update.plan is not None and user_update.plan != user.plan:
        valid_plans = [e.value for e in UserPlan]
        if user_update.plan not in valid_plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan",
            )
        changes["plan"] = {"old": user.plan, "new": user_update.plan}
        sensitive_changes["plan"] = changes["plan"]
        user.plan = user_update.plan

    if user_update.daily_limit is not None and user_update.daily_limit != user.daily_limit:
        changes["daily_limit"] = {"old": user.daily_limit, "new": user_update.daily_limit}
        user.daily_limit = user_update.daily_limit

    if user_update.is_active is not None and user_update.is_active != user.is_active:
        changes["is_active"] = {"old": user.is_active, "new": user_update.is_active}
        sensitive_changes["is_active"] = changes["is_active"]
        user.is_active = user_update.is_active

    if user_update.is_banned is not None and user_update.is_banned != user.is_banned:
        changes["is_banned"] = {"old": user.is_banned, "new": user_update.is_banned}
        sensitive_changes["is_banned"] = changes["is_banned"]
        user.is_banned = user_update.is_banned

    # Commit changes
    await db.commit()
    await db.refresh(user)

    # Log audit trail
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_USER_UPDATE,
        actor=admin,
        target_user=user,
        changes=changes,
        metadata={
            "sensitive_changes": sensitive_changes if sensitive_changes else None,
        },
    )

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user (admin only).
    
    Soft delete recommended for compliance. Hard delete requires superadmin.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Log before deletion
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.USER_DELETED,
        actor=admin,
        target_user=user,
        metadata={"deletion_type": "hard"},
    )

    # Delete user
    await db.delete(user)
    await db.commit()

    return None


# ==================== BULK OPERATIONS ====================


@router.post("/users/bulk-update", response_model=List[UserListItem])
async def bulk_update_users(
    request: Request,
    user_ids: List[int],
    updates: UserUpdate,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk update multiple users at once.
    
    Useful for:
    - Banning multiple users
    - Changing plan for a group
    - Activating/deactivating accounts
    
    Returns updated users list.
    """
    # Get all users
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = list(result.scalars().all())
    
    if len(users) != len(user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some users not found",
        )
    
    updated_users = []
    
    # Update each user
    for user in users:
        if updates.role is not None:
            user.role = updates.role
        if updates.plan is not None:
            user.plan = updates.plan
        if updates.is_active is not None:
            user.is_active = updates.is_active
        if updates.is_banned is not None:
            user.is_banned = updates.is_banned
        if updates.daily_limit is not None:
            user.daily_limit = updates.daily_limit
        
        updated_users.append(user)
    
    await db.commit()
    
    # Refresh to get updated values
    for user in updated_users:
        await db.refresh(user)
    
    # Log bulk action
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_USER_UPDATE,
        actor=admin,
        metadata={
            "bulk_operation": True,
            "affected_users": [u.id for u in updated_users],
            "updates": updates.model_dump(exclude_unset=True),
        },
    )
    
    return updated_users


@router.post("/users/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_users(
    request: Request,
    user_ids: List[int],
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk delete multiple users at once.
    
    Use with caution - this is a destructive operation.
    """
    # Get all users for logging
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = list(result.scalars().all())
    
    # Delete
    await db.execute(User.__table__.delete().where(User.id.in_(user_ids)))
    await db.commit()
    
    # Log bulk deletion
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.USER_DELETED,
        actor=admin,
        metadata={
            "bulk_operation": True,
            "deleted_count": len(users),
            "deleted_user_ids": user_ids,
        },
    )
    
    return None


# ==================== ANALYTICS ====================


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    request: Request,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics data (admin only)."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count(func.distinct(Analysis.user_id))).where(
            Analysis.created_at >= today_start
        )
    )
    active_users_today = active_users_result.scalar() or 0

    total_analyses_result = await db.execute(select(func.count(Analysis.id)))
    total_analyses = total_analyses_result.scalar() or 0

    analyses_today_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.created_at >= today_start)
    )
    analyses_today = analyses_today_result.scalar() or 0

    avg_confidence_result = await db.execute(
        select(func.avg(Analysis.confidence_score)).where(
            Analysis.status == AnalysisStatus.COMPLETED
        )
    )
    avg_confidence = avg_confidence_result.scalar() or 0.0

    failed_analyses_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.status == AnalysisStatus.FAILED)
    )
    failed_analyses = failed_analyses_result.scalar() or 0

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

    # Log analytics access
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_ANALYTICS_VIEW,
        actor=admin,
        metadata={
            "total_users": total_users,
            "total_analyses": total_analyses,
        },
    )

    return AnalyticsResponse(
        total_users=total_users,
        active_users_today=active_users_today,
        total_analyses=total_analyses,
        analyses_today=analyses_today,
        avg_confidence_score=round(float(avg_confidence), 2),
        failed_analyses=failed_analyses,
        top_users=top_users,
    )


# ==================== AUDIT LOGS ====================


@router.get("/audit-logs", response_model=CursorPaginationResponse[AuditLogListItem])
async def list_audit_logs(
    request: Request,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    event_category: Optional[str] = Query(None),
    actor_email: Optional[str] = Query(None),
    target_email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    List audit logs with filtering.
    
    Query Parameters:
    - **event_type**: Filter by specific event type
    - **event_category**: Filter by category (auth, user, admin, security, data, system)
    - **actor_email**: Filter by actor email
    - **target_email**: Filter by target email
    - **status**: Filter by status (success, failure, denied)
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    """
    query = select(AuditLog)
    
    # Apply filters
    if event_type:
        query = query.where(AuditLog.event_type == event_type)
    
    if event_category:
        query = query.where(AuditLog.event_category == event_category)
    
    if actor_email:
        query = query.where(AuditLog.actor_email.ilike(f"%{actor_email}%"))
    
    if target_email:
        query = query.where(AuditLog.target_email.ilike(f"%{target_email}%"))
    
    if status:
        query = query.where(AuditLog.status == status)
    
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0
    
    # Apply sorting and pagination
    query = query.order_by(desc(AuditLog.created_at)).limit(limit + 1)
    
    if cursor:
        import base64
        try:
            cursor_id = int(base64.b64decode(cursor).decode())
            cursor_item = await db.get(AuditLog, cursor_id)
            if cursor_item:
                query = query.where(AuditLog.created_at < cursor_item.created_at)
        except (ValueError, Exception):
            pass
    
    result = await db.execute(query)
    logs = list(result.scalars().all())
    
    has_more = len(logs) > limit
    if has_more:
        logs = logs[:limit]
    
    next_cursor = None
    if has_more and logs:
        import base64
        next_cursor = base64.b64encode(str(logs[-1].id).encode()).decode()
    
    return CursorPaginationResponse(
        data=logs,
        next_cursor=next_cursor,
        has_more=has_more,
        total_count=total_count,
    )


@router.get("/audit-logs/stats")
async def get_audit_stats(
    request: Request,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=90),
):
    """
    Get audit log statistics for the specified period.
    
    Returns:
    - Total events count
    - Events by category
    - Events by status
    - Top actors
    - Top event types
    """
    from datetime import timedelta
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total events
    total_query = select(func.count(AuditLog.id)).where(
        AuditLog.created_at >= start_date
    )
    total_result = await db.execute(total_query)
    total_events = total_result.scalar() or 0
    
    # Events by category
    category_query = select(
        AuditLog.event_category,
        func.count(AuditLog.id).label("count")
    ).where(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.event_category)
    
    category_result = await db.execute(category_query)
    events_by_category = [
        {"category": row.event_category, "count": row.count}
        for row in category_result.all()
    ]
    
    # Events by status
    status_query = select(
        AuditLog.status,
        func.count(AuditLog.id).label("count")
    ).where(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.status)
    
    status_result = await db.execute(status_query)
    events_by_status = [
        {"status": row.status, "count": row.count}
        for row in status_result.all()
    ]
    
    # Top actors
    actors_query = select(
        AuditLog.actor_email,
        func.count(AuditLog.id).label("count")
    ).where(
        AuditLog.created_at >= start_date,
        AuditLog.actor_email.isnot(None)
    ).group_by(AuditLog.actor_email).order_by(
        desc(func.count(AuditLog.id))
    ).limit(10)
    
    actors_result = await db.execute(actors_query)
    top_actors = [
        {"email": row.actor_email, "count": row.count}
        for row in actors_result.all()
    ]
    
    # Top event types
    event_types_query = select(
        AuditLog.event_type,
        func.count(AuditLog.id).label("count")
    ).where(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.event_type).order_by(
        desc(func.count(AuditLog.id))
    ).limit(10)
    
    event_types_result = await db.execute(event_types_query)
    top_event_types = [
        {"event_type": row.event_type, "count": row.count}
        for row in event_types_result.all()
    ]
    
    return {
        "total_events": total_events,
        "period_days": days,
        "events_by_category": events_by_category,
        "events_by_status": events_by_status,
        "top_actors": top_actors,
        "top_event_types": top_event_types,
    }


# ==================== ADVANCED ANALYTICS ====================


@router.get("/analytics/advanced")
async def get_advanced_analytics(
    request: Request,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=90),
):
    """
    Get advanced analytics with time series data.
    
    Returns:
    - Summary stats
    - User growth time series
    - Analysis volume time series
    - Top users, brands
    - Funnel data
    """
    from app.services.analytics_service import AnalyticsService
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    service = AnalyticsService(db)
    
    # Get all data in parallel
    summary_task = service.get_summary_stats(start_date, now)
    user_growth_task = service.get_time_series("users", start_date, now, "day")
    analysis_volume_task = service.get_time_series("analyses", start_date, now, "day")
    top_users_task = service.get_top_items("users", limit=10, start_date=start_date)
    top_brands_task = service.get_top_items("brands", limit=10, start_date=start_date)
    funnel_task = service.get_funnel_data("analysis")
    
    summary, user_growth, analysis_volume, top_users, top_brands, funnel = await asyncio.gather(
        summary_task,
        user_growth_task,
        analysis_volume_task,
        top_users_task,
        top_brands_task,
        funnel_task,
    )
    
    # Log access
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_ANALYTICS_VIEW,
        actor=admin,
        status="success",
        description="Advanced analytics viewed",
        metadata={"days": days},
    )
    
    return {
        "summary": summary,
        "user_growth": user_growth,
        "analysis_volume": analysis_volume,
        "top_users": top_users,
        "top_brands": top_brands,
        "funnel": funnel,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "days": days,
        },
    }


@router.get("/analytics/cohort")
async def get_cohort_analytics(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    cohort_size: str = Query("month", pattern="^(week|month)$"),
    periods: int = Query(12, ge=1, le=24),
):
    """Get cohort retention data."""
    from app.services.analytics_service import AnalyticsService

    service = AnalyticsService(db)
    cohort_data = await service.get_cohort_data(cohort_size, periods)

    return {
        "cohort_data": cohort_data,
        "cohort_size": cohort_size,
        "periods": periods,
    }


# ==================== DATA EXPORT ====================


@router.post("/export")
async def create_export(
    request: Request,
    export_type: str = Body(...),
    format: str = Body("csv"),
    filters: Optional[dict] = Body(None),
    columns: Optional[List[str]] = Body(None),
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create data export job.
    
    Supported types: users, analyses, audit_logs, payments
    Supported formats: csv, json, xlsx
    
    Returns export job ID for status checking.
    """
    from app.services.export_service import get_export_service, ExportJob
    
    export_service = get_export_service(db)
    
    # Create job
    job = await export_service.create_export_job(
        export_type=export_type,  # type: ignore
        format=format,  # type: ignore
        user_id=admin.id,
        filters=filters,
        columns=columns,
    )
    
    # Process asynchronously (in production, use Celery)
    asyncio.create_task(export_service.process_export(job))
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_EXPORT,
        actor=admin,
        status="success",
        description=f"Export created: {export_type}",
        metadata={"format": format},
    )
    
    return job.to_dict()


@router.get("/export/{export_id}")
async def get_export_status(
    export_id: str,
    admin: User = Depends(get_current_admin_user),
):
    """Get export job status."""
    from app.services.export_service import get_export_service
    
    export_service = get_export_service(admin)
    job = export_service.get_job(export_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found",
        )
    
    return job.to_dict()


@router.get("/export/{export_id}/download")
async def download_export(
    export_id: str,
    admin: User = Depends(get_current_admin_user),
):
    """Download export file."""
    from app.services.export_service import get_export_service

    export_service = get_export_service(admin)
    job = export_service.get_job(export_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found",
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export not completed yet",
        )
    
    if not job.file_path or not Path(job.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found",
        )
    
    return FileResponse(
        path=job.file_path,
        filename=f"{job.export_type}_{export_id}.{job.format}",
        media_type="application/octet-stream",
    )


@router.get("/exports")
async def list_exports(
    admin: User = Depends(get_current_admin_user),
    limit: int = Query(20, ge=1, le=100),
):
    """List export jobs for current user."""
    from app.services.export_service import get_export_service
    
    export_service = get_export_service(admin)
    jobs = export_service.list_jobs(admin.id, limit)
    
    return {
        "exports": [job.to_dict() for job in jobs],
        "total": len(jobs),
    }
