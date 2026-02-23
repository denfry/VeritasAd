"""
Audit Logging Service - BigTech Standard.

Provides comprehensive audit logging for all admin actions and security events.
Similar to AWS CloudTrail, Google Cloud Audit Logs, Azure Activity Log.

Features:
- Structured logging with full context
- Async database writes
- Automatic IP and user agent capture
- Change tracking for updates
- Compliance-ready retention policies
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
import structlog

from app.models.database import AuditLog, AuditEventType, User

logger = structlog.get_logger(__name__)


# Event category mapping
EVENT_CATEGORIES: Dict[AuditEventType, str] = {
    # Authentication
    AuditEventType.LOGIN: "auth",
    AuditEventType.LOGOUT: "auth",
    AuditEventType.LOGIN_FAILED: "auth",
    AuditEventType.PASSWORD_RESET: "auth",
    AuditEventType.TWO_FA_ENABLED: "auth",
    AuditEventType.TWO_FA_DISABLED: "auth",
    
    # User management
    AuditEventType.USER_CREATED: "user",
    AuditEventType.USER_UPDATED: "user",
    AuditEventType.USER_DELETED: "user",
    AuditEventType.USER_BANNED: "user",
    AuditEventType.USER_UNBANNED: "user",
    AuditEventType.USER_ACTIVATED: "user",
    AuditEventType.USER_DEACTIVATED: "user",
    AuditEventType.ROLE_CHANGED: "user",
    AuditEventType.PLAN_CHANGED: "user",
    
    # Admin actions
    AuditEventType.ADMIN_LOGIN: "admin",
    AuditEventType.ADMIN_LOGOUT: "admin",
    AuditEventType.ADMIN_USER_VIEW: "admin",
    AuditEventType.ADMIN_USER_LIST: "admin",
    AuditEventType.ADMIN_USER_UPDATE: "admin",
    AuditEventType.ADMIN_ANALYTICS_VIEW: "admin",
    AuditEventType.ADMIN_EXPORT: "admin",
    AuditEventType.ADMIN_IMPERSONATE: "admin",
    
    # Data operations
    AuditEventType.DATA_EXPORT: "data",
    AuditEventType.DATA_IMPORT: "data",
    AuditEventType.DATA_DELETE: "data",
    
    # Security
    AuditEventType.SESSION_REVOKED: "security",
    AuditEventType.API_KEY_CREATED: "security",
    AuditEventType.API_KEY_REVOKED: "security",
    AuditEventType.IP_WHITELIST_ADDED: "security",
    AuditEventType.IP_WHITELIST_REMOVED: "security",
    
    # System
    AuditEventType.SETTINGS_CHANGED: "system",
    AuditEventType.PERMISSION_GRANTED: "system",
    AuditEventType.PERMISSION_REVOKED: "system",
}


class AuditLogger:
    """
    Audit logging service for tracking all admin actions and security events.
    
    Usage:
        audit_logger = AuditLogger(db_session, request)
        await audit_logger.log(
            event_type=AuditEventType.ADMIN_USER_UPDATE,
            actor=user,
            target_user=target_user,
            changes={"role": {"old": "user", "new": "admin"}},
        )
    """
    
    def __init__(self, db_session: AsyncSession, request: Optional[Request] = None):
        self.db = db_session
        self.request = request
    
    def _get_client_ip(self) -> Optional[str]:
        """Extract client IP from request, handling proxies."""
        if not self.request:
            return None
        
        # Check X-Forwarded-For header (proxy/load balancer)
        forwarded_for = self.request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = self.request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Direct connection
        if self.request.client:
            return self.request.client.host
        
        return None
    
    def _get_user_agent(self) -> Optional[str]:
        """Extract user agent from request."""
        if not self.request:
            return None
        return self.request.headers.get("user-agent")
    
    async def log(
        self,
        event_type: AuditEventType,
        actor: Optional[User] = None,
        target_user: Optional[User] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        target_email: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (see AuditEventType)
            actor: User who performed the action
            target_user: User that was acted upon (if applicable)
            target_type: Type of target resource (e.g., "user", "analysis")
            target_id: ID of target resource
            target_email: Email of target user (for convenience)
            changes: Dict of changes for update events
            metadata: Additional context metadata
            status: Event status (success, failure, denied)
            error_message: Error message if failed
            description: Human-readable description (auto-generated if not provided)
        
        Returns:
            Created AuditLog object
        """
        # Auto-generate description if not provided
        if not description:
            description = self._generate_description(
                event_type, actor, target_user, changes
            )
        
        # Determine target info
        if target_user and not target_type:
            target_type = "user"
        if target_user and not target_id:
            target_id = target_user.id
        if target_user and not target_email:
            target_email = target_user.email
        
        # Create audit log entry
        audit_log = AuditLog(
            event_type=event_type,
            event_category=EVENT_CATEGORIES.get(event_type, "other"),
            description=description,
            actor_user_id=actor.id if actor else None,
            actor_email=actor.email if actor else None,
            actor_ip=self._get_client_ip(),
            actor_user_agent=self._get_user_agent(),
            target_type=target_type,
            target_id=target_id,
            target_email=target_email,
            changes=changes,
            metadata=metadata,
            status=status,
            error_message=error_message,
        )
        
        self.db.add(audit_log)
        
        # Flush to get ID without committing
        await self.db.flush()
        
        # Log to structured logger as well (for real-time monitoring)
        log_data = {
            "audit_event": event_type.value,
            "audit_category": EVENT_CATEGORIES.get(event_type, "other"),
            "audit_status": status,
            "actor_id": actor.id if actor else None,
            "actor_email": actor.email if actor else None,
            "target_id": target_id,
            "target_email": target_email,
        }
        
        if status == "failure" or status == "denied":
            log_data["error"] = error_message
        
        if status == "failure":
            logger.warning("audit_event_failed", **log_data)
        elif status == "denied":
            logger.warning("audit_event_denied", **log_data)
        else:
            logger.info("audit_event", **log_data)
        
        return audit_log
    
    def _generate_description(
        self,
        event_type: AuditEventType,
        actor: Optional[User],
        target_user: Optional[User],
        changes: Optional[Dict[str, Any]],
    ) -> str:
        """Generate human-readable description for the event."""
        actor_email = actor.email if actor else "unknown"
        target_email = target_user.email if target_user else None
        
        descriptions = {
            AuditEventType.LOGIN: f"User {actor_email} logged in",
            AuditEventType.LOGOUT: f"User {actor_email} logged out",
            AuditEventType.LOGIN_FAILED: f"Failed login attempt for {actor_email}",
            AuditEventType.ADMIN_USER_VIEW: f"Admin {actor_email} viewed user {target_email}",
            AuditEventType.ADMIN_USER_LIST: f"Admin {actor_email} listed users",
            AuditEventType.ADMIN_USER_UPDATE: f"Admin {actor_email} updated user {target_email}",
            AuditEventType.ADMIN_ANALYTICS_VIEW: f"Admin {actor_email} viewed analytics",
            AuditEventType.USER_BANNED: f"User {target_email} was banned by {actor_email}",
            AuditEventType.USER_UNBANNED: f"User {target_email} was unbanned by {actor_email}",
            AuditEventType.ROLE_CHANGED: f"Role changed for {target_email} by {actor_email}",
            AuditEventType.PLAN_CHANGED: f"Plan changed for {target_email} by {actor_email}",
        }
        
        base_desc = descriptions.get(event_type, f"Event {event_type.value} by {actor_email}")
        
        # Append changes if present
        if changes:
            changes_str = ", ".join(f"{k}: {v.get('old')}→{v.get('new')}" for k, v in changes.items())
            base_desc += f" ({changes_str})"
        
        return base_desc


async def get_audit_logger(
    db: AsyncSession,
    request: Optional[Request] = None,
) -> AuditLogger:
    """Dependency injection for AuditLogger."""
    return AuditLogger(db, request)


# Convenience functions for common operations
async def log_admin_action(
    db: AsyncSession,
    request: Request,
    event_type: AuditEventType,
    admin: User,
    target_user: Optional[User] = None,
    changes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> AuditLog:
    """
    Convenience function for logging admin actions.
    
    Usage:
        await log_admin_action(
            db, request,
            AuditEventType.ADMIN_USER_UPDATE,
            admin=current_user,
            target_user=target_user,
            changes={"role": {"old": "user", "new": "admin"}},
        )
    """
    audit_logger = AuditLogger(db, request)
    return await audit_logger.log(
        event_type=event_type,
        actor=admin,
        target_user=target_user,
        changes=changes,
        metadata=metadata,
        status=status,
        error_message=error_message,
    )


class AuditQuery:
    """
    Query builder for audit logs.
    
    Usage:
        logs = await AuditQuery(db)
            .filter_by_actor(user_id=123)
            .filter_by_category("admin")
            .filter_by_date_range(start, end)
            .limit(50)
            .all()
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.query = select(AuditLog)
    
    def filter_by_actor(self, user_id: int) -> "AuditQuery":
        """Filter by actor user ID."""
        self.query = self.query.where(AuditLog.actor_user_id == user_id)
        return self
    
    def filter_by_actor_email(self, email: str) -> "AuditQuery":
        """Filter by actor email."""
        self.query = self.query.where(AuditLog.actor_email == email)
        return self
    
    def filter_by_target(self, target_type: str, target_id: Optional[int] = None) -> "AuditQuery":
        """Filter by target type and optionally ID."""
        self.query = self.query.where(AuditLog.target_type == target_type)
        if target_id is not None:
            self.query = self.query.where(AuditLog.target_id == target_id)
        return self
    
    def filter_by_event_type(self, event_type: AuditEventType) -> "AuditQuery":
        """Filter by event type."""
        self.query = self.query.where(AuditLog.event_type == event_type)
        return self
    
    def filter_by_category(self, category: str) -> "AuditQuery":
        """Filter by event category."""
        self.query = self.query.where(AuditLog.event_category == category)
        return self
    
    def filter_by_date_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> "AuditQuery":
        """Filter by date range."""
        if start:
            self.query = self.query.where(AuditLog.created_at >= start)
        if end:
            self.query = self.query.where(AuditLog.created_at <= end)
        return self
    
    def filter_by_status(self, status: str) -> "AuditQuery":
        """Filter by status (success, failure, denied)."""
        self.query = self.query.where(AuditLog.status == status)
        return self
    
    def order_by_created(self, descending: bool = True) -> "AuditQuery":
        """Order by created_at timestamp."""
        order = desc(AuditLog.created_at) if descending else AuditLog.created_at
        self.query = self.query.order_by(order)
        return self
    
    def limit(self, limit: int) -> "AuditQuery":
        """Set limit."""
        self.query = self.query.limit(limit)
        return self
    
    def offset(self, offset: int) -> "AuditQuery":
        """Set offset."""
        self.query = self.query.offset(offset)
        return self
    
    async def all(self) -> List[AuditLog]:
        """Execute and return all results."""
        result = await self.db.execute(self.query)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count matching logs."""
        count_query = select(func.count()).select_from(self.query.subquery())
        result = await self.db.execute(count_query)
        return result.scalar() or 0
