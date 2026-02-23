"""Telegram domain schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class TelegramAuthRequest(BaseModel):
    """Telegram Login Widget authentication request."""

    id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    username: Optional[str] = Field(None, description="Telegram username")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")
    auth_date: int = Field(..., description="Authentication timestamp")
    hash: str = Field(..., description="HMAC-SHA256 hash for validation")


class TelegramAuthResponse(BaseModel):
    """Telegram authentication response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = "bearer"
    user_id: int = Field(..., description="User ID in database")
    telegram_id: int = Field(..., description="Telegram ID")
    is_new_user: bool = Field(..., description="True if user was just created")


class TelegramLinkRequest(BaseModel):
    """Request to link Telegram account."""

    telegram_id: int = Field(..., description="Telegram user ID")
    link_token: str = Field(..., description="Link token from bot")
    username: Optional[str] = Field(None, description="Telegram username")


class TelegramLinkResponse(BaseModel):
    """Response after linking Telegram account."""

    success: bool = True
    message: str = Field(..., description="Success message")
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None


class TelegramUnlinkResponse(BaseModel):
    """Response after unlinking Telegram account."""

    success: bool = True
    message: str = Field(..., description="Success message")
