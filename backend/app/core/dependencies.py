from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Header, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import structlog

from app.core.config import settings
from app.core.errors import AuthException, RateLimitException
from app.models.database import get_db, User, UserPlan

logger = structlog.get_logger(__name__)


async def get_current_user(
    api_key: str = Header(None, alias=settings.API_KEY_HEADER),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate API key and return current user.
    Automatically creates new user if API key doesn't exist.
    Checks rate limits and account status.
    """
    if not api_key:
        raise AuthException(
            message="API key required",
            error_code="API_KEY_REQUIRED",
        )

    # Get or create user
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if not user:
        # Auto-create new user with this API key
        user = User(
            api_key=api_key,
            plan=UserPlan.FREE,
            daily_limit=settings.FREE_TIER_DAILY_LIMIT,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info("user_created", api_key=api_key[:8] + "...", plan=user.plan)

    # Check if account is active
    if not user.is_active:
        raise AuthException(
            message="Account is inactive",
            error_code="ACCOUNT_INACTIVE",
        )

    # Check if account is banned
    if user.is_banned:
        raise AuthException(
            message="Account is banned",
            error_code="ACCOUNT_BANNED",
        )

    # Reset daily usage if new day
    now = datetime.now(timezone.utc)
    if user.last_reset_date.date() < now.date():
        user.daily_used = 0
        user.last_reset_date = now
        await db.commit()

    # Check rate limit
    if user.daily_used >= user.daily_limit:
        raise RateLimitException(
            message=f"Daily limit exceeded. Your plan: {user.plan}",
            details={
                "limit": user.daily_limit,
                "used": user.daily_used,
                "plan": user.plan,
                "reset_at": (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat(),
            },
        )

    return user


async def increment_usage(
    user: User,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Increment user's daily usage counter"""
    user.daily_used += 1
    user.total_analyses += 1
    await db.commit()


def generate_api_key() -> str:
    """Generate a new API key"""
    return secrets.token_urlsafe(settings.API_KEY_LENGTH)


# Alias for backward compatibility
get_api_key = get_current_user