"""
RBAC (Role-Based Access Control) с permissions системой.
BigTech Standard - аналог AWS IAM, Google Cloud IAM.

Permissions hierarchy:
- resource:action (e.g., "users:read", "users:write")
- Wildcards: "users:*", "*:read", "*"
"""
from enum import Enum
from typing import List, Set, Optional
from functools import wraps
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.database import User, UserRole

logger = structlog.get_logger(__name__)


class Permission(str, Enum):
    """
    Все разрешения в системе.
    Формат: resource:action
    """
    # Users management
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"
    USERS_BAN = "users:ban"
    USERS_IMPERSOATE = "users:impersonate"
    
    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Audit logs
    AUDIT_LOGS_READ = "audit-logs:read"
    AUDIT_LOGS_EXPORT = "audit-logs:export"
    
    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    
    # Admin actions
    ADMIN_ACCESS = "admin:access"
    ADMIN_IMPERSONATE = "admin:impersonate"
    
    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_WRITE = "reports:write"
    
    # All permissions (superadmin)
    ALL = "*:*"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.USER: {
        Permission.USERS_READ,  # Can read own profile
    },
    UserRole.ADMIN: {
        Permission.ADMIN_ACCESS,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.USERS_BAN,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
        Permission.AUDIT_LOGS_READ,
        Permission.AUDIT_LOGS_EXPORT,
        Permission.REPORTS_READ,
        Permission.REPORTS_WRITE,
    },
}

# Superadmin has all permissions
SUPERADMIN_PERMISSIONS = {Permission.ALL}


class PermissionDenied(Exception):
    """Raised when user doesn't have required permission."""
    pass


def check_permission(user: User, required_permission: Permission) -> bool:
    """
    Check if user has required permission.
    
    Supports:
    - Exact match
    - Wildcards (resource:*, *:action, *)
    """
    # Get user permissions
    user_permissions = get_user_permissions(user)
    
    # Check for superadmin
    if Permission.ALL in user_permissions:
        return True
    
    # Check exact match
    if required_permission in user_permissions:
        return True
    
    # Check wildcards
    resource, action = required_permission.value.split(":")
    
    # Check resource:* (e.g., "users:*")
    if Permission(f"{resource}:*") in user_permissions:
        return True
    
    # Check *:action (e.g., "*:read")
    if Permission(f"*:{action}") in user_permissions:
        return True
    
    return False


def get_user_permissions(user: User) -> Set[Permission]:
    """Get all permissions for a user based on their role."""
    if not user:
        return set()
    
    # Check for superadmin (hardcoded email or special flag)
    if user.email and user.email.endswith("@veritasad.super"):
        return SUPERADMIN_PERMISSIONS
    
    # Get permissions from role
    role_permissions = ROLE_PERMISSIONS.get(UserRole(user.role), set())
    return role_permissions.copy()


def require_permission(required_permission: Permission):
    """
    Decorator to require specific permission for an endpoint.
    
    Usage:
        @router.get("/users")
        @require_permission(Permission.USERS_READ)
        async def list_users(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs or args
            current_user = kwargs.get("current_user")
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            
            if not check_permission(current_user, required_permission):
                logger.warning(
                    "permission_denied",
                    user_id=current_user.id,
                    user_email=current_user.email,
                    required_permission=required_permission.value,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {required_permission.value}",
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """Require at least one of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            
            # Check if user has any of the required permissions
            has_permission = any(
                check_permission(current_user, perm) for perm in permissions
            )
            
            if not has_permission:
                logger.warning(
                    "permission_denied",
                    user_id=current_user.id,
                    user_email=current_user.email,
                    required_permissions=[p.value for p in permissions],
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(*permissions: Permission):
    """Require all of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            
            # Check if user has all required permissions
            has_all_permissions = all(
                check_permission(current_user, perm) for perm in permissions
            )
            
            if not has_all_permissions:
                logger.warning(
                    "permission_denied",
                    user_id=current_user.id,
                    user_email=current_user.email,
                    required_permissions=[p.value for p in permissions],
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """
    Dependency for FastAPI to check permissions.
    
    Usage:
        @router.get("/users")
        async def list_users(
            _: bool = Depends(PermissionChecker(Permission.USERS_READ)),
            current_user: User = Depends(get_current_user)
        ):
            ...
    """
    def __init__(self, *required_permissions: Permission):
        self.required_permissions = required_permissions
        self.require_all = False
    
    def require_all_perms(self) -> "PermissionChecker":
        """Require all permissions instead of any."""
        self.require_all = True
        return self
    
    async def __call__(
        self,
        request: Request,
        current_user: User = None,
    ) -> bool:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        
        if self.require_all:
            has_permission = all(
                check_permission(current_user, perm)
                for perm in self.required_permissions
            )
        else:
            has_permission = any(
                check_permission(current_user, perm)
                for perm in self.required_permissions
            )
        
        if not has_permission:
            logger.warning(
                "permission_denied",
                user_id=current_user.id,
                user_email=current_user.email,
                path=request.url.path,
                required_permissions=[p.value for p in self.required_permissions],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        
        return True
