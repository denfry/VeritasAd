"""User domain router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.domains.users.schemas import UserProfile
from app.models.database import User, get_db

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    return user
