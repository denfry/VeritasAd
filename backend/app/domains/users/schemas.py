"""User domain schemas."""
from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    """Current user profile response."""

    id: int
    email: Optional[str] = None
    supabase_user_id: Optional[str] = None
    telegram_id: Optional[int] = None
    plan: str
    role: str
    daily_limit: int
    daily_used: int
    total_analyses: int = 0
    is_active: bool
    api_key: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request."""

    email: Optional[str] = None
