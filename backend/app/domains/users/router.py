"""User domain router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
import secrets

from app.core.dependencies import get_current_user
from app.domains.users.schemas import UserProfile, UserUpdate
from app.models.database import User, Analysis, get_db

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    return user


@router.patch("/me", response_model=UserProfile)
async def update_current_user_profile(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    if payload.email is not None:
        user.email = payload.email

    await db.commit()
    await db.refresh(user)
    return user


# ==================== PREFERENCES ====================


@router.get("/me/preferences")
async def get_user_preferences(
    user: User = Depends(get_current_user),
):
    """Get user preferences stored in metadata JSON field."""
    metadata = user.metadata or {}
    return {
        "notifications": {
            "emailReports": metadata.get("notif_email_reports", True),
            "emailAlerts": metadata.get("notif_email_alerts", False),
            "pushNotifications": metadata.get("notif_push", True),
            "weeklyDigest": metadata.get("notif_weekly_digest", True),
            "analysisComplete": metadata.get("notif_analysis_complete", True),
            "securityAlerts": metadata.get("notif_security", True),
        },
        "theme": metadata.get("theme", "system"),
        "language": metadata.get("language", "en"),
    }


@router.put("/me/preferences")
async def update_user_preferences(
    payload: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences stored in metadata JSON field."""
    if user.metadata is None:
        user.metadata = {}

    allowed_notification_keys = {
        "emailReports",
        "emailAlerts",
        "pushNotifications",
        "weeklyDigest",
        "analysisComplete",
        "securityAlerts",
    }
    allowed_top_keys = {"notifications", "theme", "language"}

    notifications = payload.get("notifications", {})
    if isinstance(notifications, dict):
        for key, value in notifications.items():
            if key not in allowed_notification_keys:
                continue
            meta_key = {
                "emailReports": "notif_email_reports",
                "emailAlerts": "notif_email_alerts",
                "pushNotifications": "notif_push",
                "weeklyDigest": "notif_weekly_digest",
                "analysisComplete": "notif_analysis_complete",
                "securityAlerts": "notif_security",
            }.get(key)
            if meta_key:
                user.metadata[meta_key] = value

    if "theme" in payload and isinstance(payload["theme"], str):
        user.metadata["theme"] = payload["theme"]
    if "language" in payload and isinstance(payload["language"], str):
        user.metadata["language"] = payload["language"]

    await db.commit()
    await db.refresh(user)

    return {"status": "ok"}


# ==================== API KEY MANAGEMENT ====================


@router.get("/me/api-key")
async def get_api_key(
    user: User = Depends(get_current_user),
):
    """Get API key status (never returns the actual key)."""
    return {
        "has_key": bool(user.api_key_hash),
    }


@router.post("/me/api-key/regenerate")
async def regenerate_api_key(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key for the current user.

    Returns the plaintext key ONLY ONCE at generation time.
    Only the hash is stored in the database.
    """
    new_key = f"va_{secrets.token_urlsafe(24)}"
    key_hash = hashlib.sha256(new_key.encode()).hexdigest()

    user.api_key_hash = key_hash
    user.api_key_encrypted = None

    await db.commit()
    await db.refresh(user)

    return {
        "api_key": new_key,
        "message": "API key regenerated successfully. Store it securely -- it will not be shown again.",
    }


@router.get("/me/api-key/stats")
async def get_api_key_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get API key usage statistics from analysis history."""
    total_analyses_result = await db.execute(
        select(func.count(Analysis.id)).where(
            Analysis.user_id == user.id,
        )
    )
    total_analyses = total_analyses_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Analysis.id)).where(
            Analysis.user_id == user.id,
            Analysis.status == "completed",
        )
    )
    completed = completed_result.scalar() or 0

    return {
        "total_requests": total_analyses,
        "successful_requests": completed,
        "daily_limit": user.daily_limit,
        "daily_used": user.daily_used,
        "daily_remaining": max(0, user.daily_limit - user.daily_used),
    }
