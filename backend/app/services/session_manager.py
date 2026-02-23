"""
Session Management Service.
BigTech Standard - аналог AWS Session Manager, Google Session Security.

Features:
- Session tracking
- Session revocation
- Device fingerprinting
- Concurrent session limits
- Session activity logging
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import secrets
import structlog

from app.models.database import User, AuditLog, AuditEventType

logger = structlog.get_logger(__name__)


class SessionInfo:
    """Session information."""
    
    def __init__(
        self,
        session_id: str,
        user_id: int,
        created_at: datetime,
        last_active: datetime,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        is_current: bool = False,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.last_active = last_active
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.device_fingerprint = device_fingerprint
        self.is_current = is_current
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent[:100] + "..." if len(self.user_agent) > 100 else self.user_agent,
            "device_fingerprint": self.device_fingerprint[:16] + "..." if len(self.device_fingerprint) > 16 else self.device_fingerprint,
            "is_current": self.is_current,
        }


class SessionManager:
    """
    Manage user sessions.
    
    In production, store sessions in Redis for fast access.
    For now, we track via metadata and audit logs.
    """
    
    SESSION_TIMEOUT_DAYS = 30
    MAX_CONCURRENT_SESSIONS = 5
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def generate_device_fingerprint(
        self,
        user_agent: str,
        ip_address: str,
        accept_language: Optional[str] = None,
    ) -> str:
        """
        Generate device fingerprint from request headers.
        Not cryptographically secure, but good enough for session tracking.
        """
        fingerprint_data = f"{user_agent}|{ip_address}|{accept_language or ''}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    async def get_user_sessions(
        self,
        user: User,
        current_session_id: Optional[str] = None,
    ) -> List[SessionInfo]:
        """
        Get all active sessions for a user.
        
        In production, query Redis or sessions table.
        For now, we'll track via audit logs (login events).
        """
        # Query audit logs for login events
        query = (
            select(AuditLog)
            .where(
                AuditLog.actor_user_id == user.id,
                AuditLog.event_type.in_([
                    AuditEventType.LOGIN,
                    AuditEventType.ADMIN_LOGIN,
                ]),
            )
            .order_by(desc(AuditLog.created_at))
            .limit(20)
        )
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        sessions = []
        seen_fingerprints = set()
        
        for log in logs:
            # Create session from audit log
            fingerprint = self.generate_device_fingerprint(
                log.actor_user_agent or "",
                log.actor_ip or "",
            )
            
            # Skip duplicates (same fingerprint)
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)
            
            # Check if this is the current session
            is_current = (
                current_session_id and
                log.metadata and
                log.metadata.get("session_id") == current_session_id
            )
            
            session = SessionInfo(
                session_id=log.metadata.get("session_id", "unknown") if log.metadata else "unknown",
                user_id=user.id,
                created_at=log.created_at,
                last_active=log.created_at,
                ip_address=log.actor_ip or "unknown",
                user_agent=log.actor_user_agent or "unknown",
                device_fingerprint=fingerprint,
                is_current=is_current or (not current_session_id and not sessions),
            )
            sessions.append(session)
        
        return sessions
    
    async def revoke_session(
        self,
        user: User,
        session_id: str,
        revoked_by: User,
    ) -> bool:
        """
        Revoke a specific session.
        
        In production, remove from Redis/sessions table.
        For now, log the revocation.
        """
        logger.info(
            "session_revoked",
            user_id=user.id,
            session_id=session_id,
            revoked_by=revoked_by.id,
        )
        
        # Log audit event
        audit_log = AuditLog(
            event_type=AuditEventType.SESSION_REVOKED,
            event_category="security",
            description=f"Session {session_id[:8]}... revoked for user {user.email}",
            actor_user_id=revoked_by.id,
            actor_email=revoked_by.email,
            target_user_id=user.id,
            target_email=user.email,
            metadata={"session_id": session_id},
        )
        self.db.add(audit_log)
        await self.db.commit()
        
        return True
    
    async def revoke_all_sessions(
        self,
        user: User,
        revoked_by: User,
        exclude_current: bool = False,
    ) -> int:
        """
        Revoke all sessions for a user.
        Useful for security incidents or password changes.
        """
        sessions = await self.get_user_sessions(user)
        revoked_count = 0
        
        for session in sessions:
            if exclude_current and session.is_current:
                continue
            
            await self.revoke_session(user, session.session_id, revoked_by)
            revoked_count += 1
        
        logger.info(
            "all_sessions_revoked",
            user_id=user.id,
            revoked_count=revoked_count,
            revoked_by=revoked_by.id,
        )
        
        return revoked_count
    
    async def check_concurrent_limit(self, user: User) -> bool:
        """
        Check if user has exceeded concurrent session limit.
        Returns True if under limit, False if exceeded.
        """
        sessions = await self.get_user_sessions(user)
        return len(sessions) < self.MAX_CONCURRENT_SESSIONS
    
    async def cleanup_expired_sessions(self, user: User) -> int:
        """
        Clean up expired sessions for a user.
        """
        sessions = await self.get_user_sessions(user)
        now = datetime.now(timezone.utc)
        expired_count = 0
        
        for session in sessions:
            age = now - session.last_active
            if age > timedelta(days=self.SESSION_TIMEOUT_DAYS):
                # In production, remove from storage
                expired_count += 1
        
        return expired_count


async def get_session_manager(db: AsyncSession) -> SessionManager:
    """Dependency injection for SessionManager."""
    return SessionManager(db)
