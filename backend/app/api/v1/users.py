from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from app.models.database import get_db, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserProfile(BaseModel):
    id: int
    email: Optional[str]
    supabase_user_id: Optional[str]
    telegram_id: Optional[int]
    plan: str
    role: str
    daily_limit: int
    daily_used: int
    total_analyses: int
    is_active: bool
    api_key: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user profile.
    """
    return user
