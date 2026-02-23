"""Telegram domain service."""
import hashlib
import hmac
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import structlog

from app.core.config import settings
from app.domains.telegram.schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramUnlinkResponse,
)
from app.domains.telegram.repository import TelegramRepository
from app.models.database import User

logger = structlog.get_logger(__name__)


class TelegramAuthService:
    """Service for Telegram authentication and account linking."""

    # Hash is valid for 24 hours
    AUTH_DATA_MAX_AGE = 24 * 60 * 60  # seconds

    def __init__(self, repository: TelegramRepository):
        self.repository = repository

    def _get_bot_token_hash(self) -> bytes:
        """Get SHA256 hash of bot token for data validation."""
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        return hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

    def validate_auth_data(
        self,
        auth_data: TelegramAuthRequest,
    ) -> bool:
        """
        Validate Telegram Login Widget authentication data.

        Algorithm:
        1. Check auth_date is not older than 24 hours
        2. Remove 'hash' field from data
        3. Sort remaining fields alphabetically
        4. Create data_check_string = "key1=value1\nkey2=value2..."
        5. Compute HMAC-SHA256 with SHA256(bot_token) as key
        6. Compare with received hash

        Args:
            auth_data: Authentication data from Telegram

        Returns:
            True if validation successful

        Raises:
            ValueError: If validation fails
        """
        # 1. Check auth_date age
        now = int(time.time())
        auth_date = auth_data.auth_date

        if now - auth_date > self.AUTH_DATA_MAX_AGE:
            raise ValueError("Auth data is too old (max 24 hours)")

        # 2. Prepare data for hash validation
        data_dict = {
            "id": str(auth_data.id),
            "first_name": auth_data.first_name,
            "auth_date": str(auth_data.auth_date),
        }

        if auth_data.last_name is not None:
            data_dict["last_name"] = auth_data.last_name
        if auth_data.username is not None:
            data_dict["username"] = auth_data.username
        if auth_data.photo_url is not None:
            data_dict["photo_url"] = auth_data.photo_url

        # 3. Sort and create data_check_string
        sorted_keys = sorted(data_dict.keys())
        data_check_string = "\n".join(
            f"{key}={data_dict[key]}" for key in sorted_keys
        )

        # 4. Compute HMAC-SHA256
        token_hash = self._get_bot_token_hash()
        computed_hash = hmac.new(
            token_hash,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # 5. Compare hashes
        if not hmac.compare_digest(computed_hash, auth_data.hash):
            raise ValueError("Invalid hash")

        return True

    async def authenticate(
        self,
        auth_data: TelegramAuthRequest,
    ) -> TelegramAuthResponse:
        """
        Authenticate user with Telegram Login Widget data.

        Args:
            auth_data: Validated authentication data from Telegram

        Returns:
            Authentication response with JWT tokens

        Raises:
            ValueError: If authentication fails
        """
        # Validate auth data
        self.validate_auth_data(auth_data)

        # Get or create user
        user = await self.repository.create_or_get_user_by_telegram(
            telegram_id=auth_data.id,
            username=auth_data.username,
            first_name=auth_data.first_name,
            last_name=auth_data.last_name,
        )

        # Generate JWT tokens
        from app.core.dependencies import generate_jwt_tokens
        access_token, refresh_token = generate_jwt_tokens(
            user_id=user.id,
            email=user.email,
            telegram_id=user.telegram_id,
        )

        return TelegramAuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            telegram_id=user.telegram_id,
            is_new_user=user.total_analyses == 0,
        )

    async def link_account(
        self,
        current_user: User,
        link_request: TelegramLinkRequest,
    ) -> TelegramLinkResponse:
        """
        Link Telegram account to existing user account.

        Args:
            current_user: Currently authenticated user
            link_request: Link request with token and Telegram ID

        Returns:
            Link response

        Raises:
            ValueError: If linking fails
        """
        # Check if Telegram ID is already linked to another user
        existing_user = await self.repository.get_user_by_telegram_id(
            link_request.telegram_id
        )

        if existing_user and existing_user.id != current_user.id:
            raise ValueError(
                "This Telegram account is already linked to another user"
            )

        # Verify link token
        token_user = await self.repository.get_user_by_link_token(
            link_request.link_token
        )

        if not token_user or token_user.id != current_user.id:
            raise ValueError("Invalid or expired link token")

        # Link accounts
        user = await self.repository.link_telegram_account(
            user=current_user,
            telegram_id=link_request.telegram_id,
            username=link_request.username,
        )

        return TelegramLinkResponse(
            success=True,
            message="Telegram account successfully linked",
            telegram_id=user.telegram_id,
            telegram_username=user.telegram_username,
        )

    async def unlink_account(
        self,
        user: User,
    ) -> TelegramUnlinkResponse:
        """
        Unlink Telegram account from user.

        Args:
            user: User to unlink

        Returns:
            Unlink response

        Raises:
            ValueError: If user doesn't have linked Telegram
        """
        if not user.telegram_id:
            raise ValueError("No Telegram account is linked")

        await self.repository.unlink_telegram_account(user)

        return TelegramUnlinkResponse(
            success=True,
            message="Telegram account successfully unlinked",
        )

    async def generate_link_token(
        self,
        user: User,
    ) -> str:
        """
        Generate link token for Telegram account binding.

        Args:
            user: User to generate token for

        Returns:
            Link token
        """
        return await self.repository.generate_link_token(user)

    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
    ) -> Optional[User]:
        """Get user by Telegram ID."""
        return await self.repository.get_user_by_telegram_id(telegram_id)
