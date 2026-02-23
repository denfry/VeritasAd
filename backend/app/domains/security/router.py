"""
Security & Admin Settings Router.

Endpoints for:
- Two-Factor Authentication (2FA)
- Session management
- IP whitelist/blacklist management
- Security settings
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.dependencies import get_current_user, get_db, get_current_admin_user
from app.models.database import User
from app.services.two_factor_auth import TwoFactorAuthService
from app.services.session_manager import SessionManager, get_session_manager
from app.middleware.ip_whitelist import (
    add_to_blacklist,
    remove_from_blacklist,
    add_to_whitelist,
    remove_from_whitelist,
    get_blocked_ips,
    get_whitelisted_ips,
)
from app.middleware.admin_rate_limit import (
    check_login_attempt,
    reset_login_attempts,
    get_remaining_login_attempts,
)
from app.services.audit_logger import AuditLogger, AuditEventType

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/security", tags=["security"])


# ==================== TWO-FACTOR AUTHENTICATION ====================


@router.post("/2fa/enable")
async def enable_2fa(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable 2FA for current user.
    
    Returns:
    - secret: TOTP secret (for manual entry)
    - qr_code: Base64 encoded QR code PNG
    - provisioning_uri: OTP Auth URI
    
    User must call /2fa/confirm with a valid code to complete setup.
    """
    service = TwoFactorAuthService(db)
    secret, qr_code_base64 = await service.enable_2fa(current_user)
    
    # Log attempt
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.TWO_FA_ENABLED,
        actor=current_user,
        status="pending",
        description="2FA setup initiated",
    )
    
    return {
        "secret": secret,
        "qr_code": qr_code_base64,
        "provisioning_uri": f"otpauth://totp/{current_user.email or f'user_{current_user.id}'}?secret={secret}",
        "status": "pending_confirmation",
    }


@router.post("/2fa/confirm")
async def confirm_2fa(
    request: Request,
    code: str = Body(..., embed=True),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm 2FA setup with TOTP code.
    
    After confirmation, 2FA is enabled and backup codes are returned.
    Save backup codes securely - they won't be shown again!
    """
    service = TwoFactorAuthService(db)
    success = await service.confirm_2fa(current_user, code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    # Get backup codes (only shown once!)
    backup_codes = (current_user.user_metadata or {}).get("2fa_backup_codes_plain", [])

    # Log success
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.TWO_FA_ENABLED,
        actor=current_user,
        status="success",
        description="2FA enabled successfully",
    )
    
    return {
        "status": "enabled",
        "backup_codes": backup_codes,
        "warning": "Save these backup codes securely. They won't be shown again!",
    }


@router.post("/2fa/disable")
async def disable_2fa(
    request: Request,
    code: str = Body(..., embed=True),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable 2FA for current user.
    Requires current TOTP code for security.
    """
    service = TwoFactorAuthService(db)
    success = await service.disable_2fa(current_user, code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.TWO_FA_DISABLED,
        actor=current_user,
        status="success",
        description="2FA disabled",
    )
    
    return {"status": "disabled"}


@router.get("/2fa/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get 2FA status for current user."""
    service = TwoFactorAuthService(db)
    return await service.get_2fa_status(current_user)


@router.post("/2fa/backup-codes/regenerate")
async def regenerate_backup_codes(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate 2FA backup codes.
    Old codes will be invalidated.
    """
    service = TwoFactorAuthService(db)
    backup_codes = await service.regenerate_backup_codes(current_user)
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.TWO_FA_ENABLED,
        actor=current_user,
        status="success",
        description="2FA backup codes regenerated",
        metadata={"codes_count": len(backup_codes)},
    )
    
    return {
        "backup_codes": backup_codes,
        "warning": "Save these backup codes securely. Old codes are now invalid!",
    }


# ==================== SESSION MANAGEMENT ====================


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all active sessions for current user.
    """
    manager = await get_session_manager(db)
    sessions = await manager.get_user_sessions(current_user)
    
    return {
        "sessions": [s.to_dict() for s in sessions],
        "total": len(sessions),
    }


@router.post("/sessions/{session_id}/revoke")
async def revoke_session(
    request: Request,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session.
    Admin can revoke any user's session by providing user_id query param.
    """
    manager = await get_session_manager(db)
    
    # Check if admin is revoking for another user
    target_user = current_user
    
    success = await manager.revoke_session(target_user, session_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke session",
        )
    
    return {"status": "revoked", "session_id": session_id}


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke all sessions except current one.
    Useful for security incidents.
    """
    manager = await get_session_manager(db)
    revoked_count = await manager.revoke_all_sessions(
        current_user,
        current_user,
        exclude_current=True,
    )
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.SESSION_REVOKED,
        actor=current_user,
        status="success",
        description=f"Revoked {revoked_count} sessions",
        metadata={"revoked_count": revoked_count},
    )
    
    return {
        "status": "revoked",
        "revoked_count": revoked_count,
    }


# ==================== IP WHITELIST/BLACKLIST (ADMIN ONLY) ====================


@router.get("/ip-whitelist", dependencies=[Depends(get_current_admin_user)])
async def get_ip_whitelist():
    """Get list of whitelisted IPs."""
    return {
        "whitelist": get_whitelisted_ips(),
    }


@router.post("/ip-whitelist", dependencies=[Depends(get_current_admin_user)])
async def add_ip_to_whitelist(
    request: Request,
    ip: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    """Add IP to whitelist."""
    add_to_whitelist(ip)
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.IP_WHITELIST_ADDED,
        actor=getattr(request.state, "current_user", None),
        status="success",
        description=f"Added {ip} to whitelist",
    )
    
    return {"status": "added", "ip": ip}


@router.delete("/ip-whitelist/{ip}", dependencies=[Depends(get_current_admin_user)])
async def remove_ip_from_whitelist(
    request: Request,
    ip: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove IP from whitelist."""
    remove_from_whitelist(ip)
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.IP_WHITELIST_REMOVED,
        actor=getattr(request.state, "current_user", None),
        status="success",
        description=f"Removed {ip} from whitelist",
    )
    
    return {"status": "removed", "ip": ip}


@router.get("/ip-blacklist", dependencies=[Depends(get_current_admin_user)])
async def get_ip_blacklist():
    """Get list of blacklisted IPs."""
    return {
        "blacklist": get_blocked_ips(),
    }


@router.post("/ip-blacklist", dependencies=[Depends(get_current_admin_user)])
async def add_ip_to_blacklist_endpoint(
    request: Request,
    ip: str = Body(..., embed=True),
):
    """Add IP to blacklist."""
    add_to_blacklist(ip)
    return {"status": "added", "ip": ip}


@router.delete("/ip-blacklist/{ip}", dependencies=[Depends(get_current_admin_user)])
async def remove_ip_from_blacklist(
    ip: str,
):
    """Remove IP from blacklist."""
    remove_from_blacklist(ip)
    return {"status": "removed", "ip": ip}


# ==================== BRUTE FORCE STATUS ====================


@router.get("/brute-force/status/{identifier}")
async def get_brute_force_status(
    identifier: str,
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get brute force protection status for an identifier (email/IP).
    Admin only.
    """
    remaining = get_remaining_login_attempts(identifier)
    is_locked = remaining == 0
    
    return {
        "identifier": identifier,
        "remaining_attempts": remaining,
        "is_locked": is_locked,
        "max_attempts": 5,
    }


@router.post("/brute-force/reset/{identifier}")
async def reset_brute_force(
    request: Request,
    identifier: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset brute force lockout for an identifier.
    Admin only.
    """
    reset_login_attempts(identifier)
    
    # Log
    audit_logger = AuditLogger(db, request)
    await audit_logger.log(
        event_type=AuditEventType.ADMIN_USER_UPDATE,
        actor=current_user,
        status="success",
        description=f"Reset brute force lockout for {identifier}",
    )
    
    return {"status": "reset", "identifier": identifier}
