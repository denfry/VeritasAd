"""Admin domain schemas - BigTech Standard.

Includes:
- User management schemas
- Audit log schemas
- Analytics schemas
- Pagination schemas (cursor-based)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict


# ==================== PAGINATION ====================


T = TypeVar('T')


class CursorPaginationResponse(BaseModel, Generic[T]):
    """
    Cursor-based pagination response - BigTech standard.
    Similar to GitHub API, Stripe API, Twitter API.
    
    Attributes:
        data: List of items
        next_cursor: Cursor for next page (base64 encoded)
        has_more: Whether more results exist
        total_count: Total matching items (expensive query, optional)
    """
    data: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class OffsetPaginationRequest(BaseModel):
    """Offset-based pagination for simple cases."""
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


# ==================== USER MANAGEMENT ====================


class UserListItem(BaseModel):
    """User list item for admin."""

    id: int
    email: Optional[str] = None
    supabase_user_id: Optional[str] = None
    plan: str
    role: str
    daily_limit: int
    daily_used: int
    total_analyses: int
    is_active: bool
    is_banned: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserListItem):
    """Detailed user information for admin view."""
    
    # Additional details only visible to admins
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    api_key_created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """User update payload for admin."""

    role: Optional[str] = Field(None, description="User role (user, admin)")
    plan: Optional[str] = Field(None, description="Subscription plan (free, pro, enterprise)")
    daily_limit: Optional[int] = Field(None, ge=1, description="Daily API limit")
    is_active: Optional[bool] = Field(None, description="Account active status")
    is_banned: Optional[bool] = Field(None, description="Account banned status")


class UserBulkUpdate(BaseModel):
    """Bulk update payload for multiple users."""
    
    user_ids: List[int] = Field(..., min_length=1, max_length=100)
    updates: UserUpdate


class UserListFilters(BaseModel):
    """User list query filters."""
    
    search: Optional[str] = Field(None, description="Search by email or ID")
    plan: Optional[str] = Field(None, description="Filter by plan")
    role: Optional[str] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_banned: Optional[bool] = Field(None, description="Filter by banned status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")


# ==================== AUDIT LOGS ====================


class AuditLogListItem(BaseModel):
    """Audit log list item."""
    
    id: int
    event_type: str
    event_category: str
    description: str
    actor_user_id: Optional[int] = None
    actor_email: Optional[str] = None
    actor_ip: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_email: Optional[str] = None
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogDetail(AuditLogListItem):
    """Detailed audit log entry."""
    
    actor_user_agent: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AuditLogFilters(BaseModel):
    """Audit log query filters."""
    
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    actor_email: Optional[str] = None
    target_email: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditLogStats(BaseModel):
    """Audit log statistics."""
    
    total_events: int
    period_days: int
    events_by_category: List[Dict[str, Any]]
    events_by_status: List[Dict[str, Any]]
    top_actors: List[Dict[str, Any]]
    top_event_types: List[Dict[str, Any]]


# ==================== ANALYTICS ====================


class AnalyticsResponse(BaseModel):
    """Analytics overview response."""

    total_users: int
    active_users_today: int
    total_analyses: int
    analyses_today: int
    avg_confidence_score: float
    failed_analyses: int
    top_users: List[Dict[str, Any]]


class AnalyticsTimeSeriesPoint(BaseModel):
    """Time series data point for charts."""
    
    timestamp: datetime
    value: int
    label: Optional[str] = None


class AnalyticsTimeSeriesResponse(BaseModel):
    """Time series analytics response."""
    
    data: List[AnalyticsTimeSeriesPoint]
    start_date: datetime
    end_date: datetime
    interval: str  # hour, day, week, month


class AnalyticsDetailed(BaseModel):
    """Detailed analytics with time series."""
    
    summary: AnalyticsResponse
    user_growth: AnalyticsTimeSeriesResponse
    analysis_volume: AnalyticsTimeSeriesResponse
    error_rate: AnalyticsTimeSeriesResponse
    top_features: List[Dict[str, Any]]


# ==================== EXPORT ====================


class ExportRequest(BaseModel):
    """Data export request."""
    
    export_type: str = Field(..., description="Type of data to export (users, audit_logs, analyses)")
    format: str = Field("csv", description="Export format (csv, json, xlsx)")
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None


class ExportResponse(BaseModel):
    """Export job response."""
    
    export_id: str
    status: str  # pending, processing, completed, failed
    format: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ExportListItem(BaseModel):
    """Export job list item."""
    
    export_id: str
    export_type: str
    format: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
