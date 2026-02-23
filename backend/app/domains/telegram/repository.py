"""Telegram domain repository."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.database import User

logger = structlog.get_logger(__name__)


class TelegramRepository:
    """Repository for Telegram-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
    ) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_link_token(
        self,
        link_token: str,
    ) -> Optional[User]:
        """Get user by Telegram link token."""
        result = await self.db.execute(
            select(User).where(User.telegram_link_token == link_token)
        )
        return result.scalar_one_or_none()

    async def get_user_by_api_key_hash(
        self,
        api_key_hash: str,
    ) -> Optional[User]:
        """Get user by API key hash (for bot authentication)."""
        result = await self.db.execute(
            select(User).where(User.api_key_hash == api_key_hash)
        )
        return result.scalar_one_or_none()

    async def link_telegram_account(
        self,
        user: User,
        telegram_id: int,
        username: Optional[str] = None,
    ) -> User:
        """Link Telegram account to user."""
        user.telegram_id = telegram_id
        user.telegram_username = username
        user.telegram_linked_at = datetime.now(timezone.utc)
        user.telegram_link_token = None  # Clear link token

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "telegram_account_linked",
            user_id=user.id,
            telegram_id=telegram_id,
            username=username,
        )

        return user

    async def unlink_telegram_account(
        self,
        user: User,
    ) -> User:
        """Unlink Telegram account from user."""
        user.telegram_id = None
        user.telegram_username = None
        user.telegram_linked_at = None
        user.telegram_link_token = None

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "telegram_account_unlinked",
            user_id=user.id,
        )

        return user

    async def create_or_get_user_by_telegram(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Create new user or get existing user by Telegram ID."""
        # Check if user exists
        user = await self.get_user_by_telegram_id(telegram_id)

        if user:
            # Update username if changed
            if username and user.telegram_username != username:
                user.telegram_username = username
                await self.db.commit()
            return user

        # Create new user
        from app.models.database import UserPlan, UserRole
        from app.core.dependencies import hash_api_key
        import secrets

        # Generate API key and hash for bot authentication
        api_key = secrets.token_urlsafe(32)
        api_key_hash = hash_api_key(api_key)

        user = User(
            telegram_id=telegram_id,
            telegram_username=username,
            api_key_hash=api_key_hash,
            plan=UserPlan.FREE,
            role=UserRole.USER,
            daily_limit=100,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "user_created_from_telegram",
            user_id=user.id,
            telegram_id=telegram_id,
            username=username,
        )

        return user

    async def generate_link_token(
        self,
        user: User,
    ) -> str:
        """Generate unique link token for Telegram account binding."""
        import secrets

        token = secrets.token_urlsafe(32)
        user.telegram_link_token = token
        user.telegram_linked_at = datetime.now(timezone.utc)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "link_token_generated",
            user_id=user.id,
        )

        return token
