"""Telegram authentication and account linking API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.dependencies import get_current_user, generate_jwt_tokens
from app.domains.telegram.service import TelegramAuthService
from app.domains.telegram.repository import TelegramRepository
from app.domains.telegram.schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramUnlinkResponse,
)
from app.models.database import get_db, User
from app.utils.telegram_auth import TelegramAuthValidator

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/telegram", tags=["Telegram"])


def get_telegram_service(db: AsyncSession) -> TelegramAuthService:
    """Get Telegram service instance."""
    repository = TelegramRepository(db)
    return TelegramAuthService(repository)


@router.post(
    "/auth",
    response_model=TelegramAuthResponse,
    summary="Telegram Login Widget Authentication",
)
async def telegram_auth(
    auth_data: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with Telegram Login Widget data.

    This endpoint receives authentication data from Telegram Login Widget
    and returns JWT tokens for accessing the API.

    **Process:**
    1. Validate HMAC-SHA256 hash
    2. Check auth_date (max 24 hours old)
    3. Get or create user by Telegram ID
    4. Generate JWT tokens

    **Required fields in auth_data:**
    - `id`: Telegram user ID
    - `first_name`: User's first name
    - `auth_date`: Authentication timestamp
    - `hash`: HMAC-SHA256 signature

    **Optional fields:**
    - `last_name`: User's last name
    - `username`: Telegram username
    - `photo_url`: Profile photo URL
    """
    service = get_telegram_service(db)

    try:
        response = await service.authenticate(auth_data)
        return response
    except ValueError as e:
        logger.warning("telegram_auth_failed", reason=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("telegram_auth_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed",
        )


@router.post(
    "/link",
    response_model=TelegramLinkResponse,
    summary="Link Telegram Account",
)
async def link_telegram_account(
    link_request: TelegramLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Link Telegram account to existing user account.

    **Flow:**
    1. User requests link token from `/telegram/link-token`
    2. User opens Telegram bot with `/start {token}`
    3. Bot sends telegram_id and token to this endpoint
    4. Accounts are linked

    **Requirements:**
    - Must be authenticated with JWT or API key
    - Valid link token (generated within 24 hours)
    - Telegram ID not already linked to another account
    """
    service = get_telegram_service(db)

    try:
        response = await service.link_account(current_user, link_request)
        return response
    except ValueError as e:
        logger.warning("telegram_link_failed", reason=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("telegram_link_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link account",
        )


@router.post(
    "/unlink",
    response_model=TelegramUnlinkResponse,
    summary="Unlink Telegram Account",
)
async def unlink_telegram_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unlink Telegram account from user account.

    **Requirements:**
    - Must be authenticated
    - Must have a linked Telegram account

    **Note:** This does not delete the user account, only removes the link.
    The user can still log in with email/password or re-link Telegram.
    """
    service = get_telegram_service(db)

    try:
        response = await service.unlink_account(current_user)
        return response
    except ValueError as e:
        logger.warning("telegram_unlink_failed", reason=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("telegram_unlink_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink account",
        )


@router.post(
    "/link-token",
    response_model=dict,
    summary="Generate Link Token",
)
async def generate_link_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a token for linking Telegram account.

    **Usage:**
    1. Call this endpoint to get a link token
    2. Open Telegram bot with `/start {token}`
    3. Bot will link your account automatically

    **Token validity:** 24 hours

    **Returns:**
    - `token`: Link token to use in bot
    - `expires_in`: Token validity in seconds (86400 = 24 hours)
    """
    service = get_telegram_service(db)

    try:
        token = await service.generate_link_token(current_user)
        return {
            "token": token,
            "expires_in": 86400,  # 24 hours
        }
    except Exception as e:
        logger.exception("link_token_generation_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate link token",
        )


@router.get(
    "/status",
    response_model=dict,
    summary="Get Telegram Link Status",
)
async def get_telegram_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current Telegram account link status.

    **Returns:**
    - `is_linked`: True if Telegram account is linked
    - `telegram_id`: Telegram user ID (if linked)
    - `telegram_username`: Telegram username (if linked)
    - `linked_at`: Link timestamp (if linked)
    """
    return {
        "is_linked": current_user.telegram_id is not None,
        "telegram_id": current_user.telegram_id,
        "telegram_username": current_user.telegram_username,
        "linked_at": current_user.telegram_linked_at,
    }
