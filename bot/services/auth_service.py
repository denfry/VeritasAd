"""Telegram bot authentication service."""
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
import httpx

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    user_id: Optional[int] = None
    telegram_id: Optional[int] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    error: Optional[str] = None


class BotAuthService:
    """Service for bot authentication and account linking."""

    def __init__(self, api_url: str = None):
        self.api_url = (api_url or settings.API_URL).rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def link_account(
        self,
        telegram_id: int,
        link_token: str,
        username: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Link Telegram account to website account.

        Args:
            telegram_id: Telegram user ID
            link_token: Link token from user
            username: Telegram username (optional)

        Returns:
            Tuple of (success, error_message)
        """
        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.api_url}/api/v1/telegram/link",
                json={
                    "telegram_id": telegram_id,
                    "link_token": link_token,
                    "username": username,
                },
            )

            if response.status_code == 200:
                logger.info(f"Telegram account linked: telegram_id={telegram_id}")
                return True, None

            error_data = response.json()
            error_msg = error_data.get("detail", "Failed to link account")
            logger.warning(f"Failed to link account: {error_msg}")
            return False, error_msg

        except httpx.RequestError as e:
            logger.error(f"Request error linking account: {e}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.exception(f"Unexpected error linking account: {e}")
            return False, "Internal server error"

    async def check_account_status(
        self,
        telegram_id: int,
    ) -> dict:
        """
        Check if Telegram account is linked.

        Args:
            telegram_id: Telegram user ID

        Returns:
            Account status dict
        """
        # Use API key for authentication (tg_{telegram_id})
        api_key = f"tg_{telegram_id}"

        client = await self._get_client()

        try:
            response = await client.get(
                f"{self.api_url}/api/v1/telegram/status",
                headers={"X-API-Key": api_key},
            )

            if response.status_code == 200:
                return response.json()

            return {"is_linked": False, "error": "Not authenticated"}

        except httpx.RequestError as e:
            logger.error(f"Request error checking status: {e}")
            return {"is_linked": False, "error": str(e)}
        except Exception as e:
            logger.exception(f"Unexpected error checking status: {e}")
            return {"is_linked": False, "error": "Internal server error"}

    async def get_user_profile(
        self,
        telegram_id: int,
    ) -> Optional[dict]:
        """
        Get user profile from backend.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User profile dict or None
        """
        api_key = f"tg_{telegram_id}"
        client = await self._get_client()

        try:
            response = await client.get(
                f"{self.api_url}/api/v1/users/me",
                headers={"X-API-Key": api_key},
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None

    async def unlink_account(
        self,
        telegram_id: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Unlink Telegram account from website.

        Args:
            telegram_id: Telegram user ID

        Returns:
            Tuple of (success, error_message)
        """
        api_key = f"tg_{telegram_id}"
        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.api_url}/api/v1/telegram/unlink",
                headers={"X-API-Key": api_key},
            )

            if response.status_code == 200:
                logger.info(f"Telegram account unlinked: telegram_id={telegram_id}")
                return True, None

            error_data = response.json()
            error_msg = error_data.get("detail", "Failed to unlink account")
            return False, error_msg

        except httpx.RequestError as e:
            logger.error(f"Request error unlinking account: {e}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.exception(f"Unexpected error unlinking account: {e}")
            return False, "Internal server error"
