"""Telegram authentication utilities."""
import hashlib
import hmac
import time
from typing import Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TelegramAuthValidator:
    """
    Utility class for validating Telegram Login Widget data.

    Telegram sends authentication data with an HMAC-SHA256 signature
    that must be verified to ensure the data hasn't been tampered with.

    Reference: https://core.telegram.org/widgets/login#checking-authorization
    """

    # Hash is valid for 24 hours
    MAX_AUTH_AGE_SECONDS = 24 * 60 * 60

    @classmethod
    def validate(
        cls,
        auth_data: Dict[str, Any],
        bot_token: Optional[str] = None,
    ) -> bool:
        """
        Validate Telegram authentication data.

        Args:
            auth_data: Dictionary with Telegram auth data (id, first_name, hash, etc.)
            bot_token: Telegram bot token (defaults to settings.TELEGRAM_BOT_TOKEN)

        Returns:
            True if validation successful

        Raises:
            ValueError: If validation fails with reason
        """
        bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN

        if not bot_token:
            raise ValueError("Telegram bot token is not configured")

        # Check required fields
        required_fields = ["id", "first_name", "auth_date", "hash"]
        for field in required_fields:
            if field not in auth_data:
                raise ValueError(f"Missing required field: {field}")

        # 1. Check auth_date age
        auth_date = int(auth_data["auth_date"])
        now = int(time.time())

        if now - auth_date > cls.MAX_AUTH_AGE_SECONDS:
            raise ValueError("Auth data is too old (max 24 hours)")

        # 2. Extract hash
        received_hash = auth_data["hash"]

        # 3. Prepare data for hash computation (all fields except 'hash')
        data_dict = {
            key: value
            for key, value in auth_data.items()
            if key != "hash" and value is not None
        }

        # Convert all values to strings
        data_dict = {key: str(value) for key, value in data_dict.items()}

        # 4. Sort keys alphabetically and create data_check_string
        sorted_keys = sorted(data_dict.keys())
        data_check_string = "\n".join(
            f"{key}={data_dict[key]}" for key in sorted_keys
        )

        # 5. Compute HMAC-SHA256 with SHA256(bot_token) as key
        token_hash = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(
            token_hash,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # 6. Compare hashes securely
        if not hmac.compare_digest(computed_hash, received_hash):
            raise ValueError("Invalid hash - data may have been tampered with")

        return True

    @classmethod
    def is_auth_data_expired(
        cls,
        auth_data: Dict[str, Any],
        max_age: int = MAX_AUTH_AGE_SECONDS,
    ) -> bool:
        """
        Check if authentication data has expired.

        Args:
            auth_data: Telegram auth data
            max_age: Maximum age in seconds (default: 24 hours)

        Returns:
            True if expired
        """
        if "auth_date" not in auth_data:
            return True

        auth_date = int(auth_data["auth_date"])
        now = int(time.time())

        return now - auth_date > max_age

    @classmethod
    def extract_user_info(
        cls,
        auth_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract user information from Telegram auth data.

        Args:
            auth_data: Validated Telegram auth data

        Returns:
            Dictionary with user information
        """
        return {
            "telegram_id": int(auth_data.get("id")),
            "first_name": auth_data.get("first_name"),
            "last_name": auth_data.get("last_name"),
            "username": auth_data.get("username"),
            "photo_url": auth_data.get("photo_url"),
            "language_code": auth_data.get("language_code"),
        }


def validate_telegram_auth(
    auth_data: Dict[str, Any],
    bot_token: Optional[str] = None,
) -> bool:
    """
    Convenience function to validate Telegram auth data.

    Args:
        auth_data: Dictionary with Telegram auth data
        bot_token: Telegram bot token (optional)

    Returns:
        True if validation successful

    Raises:
        ValueError: If validation fails
    """
    return TelegramAuthValidator.validate(auth_data, bot_token)


def extract_telegram_user_info(
    auth_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function to extract user info from Telegram auth data.

    Args:
        auth_data: Telegram auth data

    Returns:
        Dictionary with user information
    """
    return TelegramAuthValidator.extract_user_info(auth_data)
