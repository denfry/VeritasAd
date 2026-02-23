"""
Rate Limiting Middleware for Admin Endpoints.
BigTech Standard - аналог AWS WAF Rate-based Rules, Google Cloud Armor.

Provides stricter rate limits for admin/sensitive endpoints.
"""
from typing import Optional, Dict, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from collections import defaultdict
from datetime import datetime, timedelta
import time
import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """
    In-memory rate limiter with sliding window.
    For production, use Redis-based limiter.
    """
    
    def __init__(self):
        # {ip: [(timestamp, count)]}
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        """
        Check if request is allowed.
        
        Returns:
            (allowed, remaining, reset_seconds)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        self.requests[key] = [
            ts for ts in self.requests[key]
            if ts > window_start
        ]
        
        # Check limit
        current_count = len(self.requests[key])
        remaining = max(0, limit - current_count)
        
        if current_count >= limit:
            # Calculate reset time
            oldest = min(self.requests[key]) if self.requests[key] else now
            reset_seconds = int((oldest + window_seconds) - now)
            return False, 0, max(1, reset_seconds)
        
        # Record request
        self.requests[key].append(now)
        
        return True, remaining, window_seconds


# Global rate limiters
_admin_limiter = RateLimiter()
_auth_limiter = RateLimiter()
_general_limiter = RateLimiter()


class AdminRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for admin endpoints.
    
    Stricter limits than general API:
    - Admin endpoints: 30 requests/minute
    - Auth endpoints: 10 requests/minute (brute force protection)
    - General API: 60 requests/minute
    """
    
    def __init__(
        self,
        app: ASGIApp,
        admin_limit: int = 30,
        admin_window: int = 60,
        auth_limit: int = 10,
        auth_window: int = 60,
        general_limit: int = 60,
        general_window: int = 60,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.enabled = enabled
        self.admin_limit = admin_limit
        self.admin_window = admin_window
        self.auth_limit = auth_limit
        self.auth_window = auth_window
        self.general_limit = general_limit
        self.general_window = general_window
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Uses IP + User ID for authenticated requests.
        """
        # Get IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        elif request.client:
            ip = request.client.host
        else:
            ip = "unknown"
        
        # Get user ID from state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            return f"user:{user_id}:{ip}"
        return f"ip:{ip}"
    
    def _get_rate_limit_config(self, path: str) -> tuple[int, int, RateLimiter]:
        """
        Get rate limit configuration for path.
        
        Returns:
            (limit, window, limiter)
        """
        # Auth endpoints - strictest limits
        if any(p in path for p in ["/auth/", "/login", "/register", "/token"]):
            return self.auth_limit, self.auth_window, _auth_limiter
        
        # Admin endpoints - strict limits
        if "/admin" in path:
            return self.admin_limit, self.admin_window, _admin_limiter
        
        # General API
        return self.general_limit, self.general_window, _general_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Get client identifier
        client_key = self._get_client_identifier(request)
        
        # Get rate limit config for this path
        limit, window, limiter = self._get_rate_limit_config(request.url.path)
        
        # Check rate limit
        allowed, remaining, reset_seconds = limiter.is_allowed(
            client_key,
            limit,
            window,
        )
        
        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                client_key=client_key,
                path=request.url.path,
                limit=limit,
                window=window,
                reset_seconds=reset_seconds,
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "limit": limit,
                    "window_seconds": window,
                    "retry_after": reset_seconds,
                },
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + reset_seconds),
                },
            )
        
        # Continue with rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(window)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset_seconds)
        
        return response


class BruteForceProtection:
    """
    Brute force protection for login attempts.
    More aggressive than general rate limiting.
    """
    
    def __init__(self):
        # {identifier: (count, first_attempt_time, locked_until)}
        self.attempts: Dict[str, tuple[int, float, Optional[float]]] = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.window_seconds = 60  # 1 minute window
    
    def check_login_attempt(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if login attempt is allowed.
        
        Returns:
            (allowed, lockout_seconds)
        """
        now = time.time()
        
        if identifier in self.attempts:
            count, first_attempt, locked_until = self.attempts[identifier]
            
            # Check if locked
            if locked_until and now < locked_until:
                return False, int(locked_until - now)
            
            # Reset if window expired
            if now - first_attempt > self.window_seconds:
                self.attempts[identifier] = (1, now, None)
                return True, None
            
            # Increment count
            if count >= self.max_attempts:
                # Lock out
                locked_until = now + self.lockout_duration
                self.attempts[identifier] = (count, first_attempt, locked_until)
                return False, self.lockout_duration
            
            self.attempts[identifier] = (count + 1, first_attempt, None)
            return True, None
        
        # First attempt
        self.attempts[identifier] = (1, now, None)
        return True, None
    
    def reset_attempts(self, identifier: str) -> None:
        """Reset attempts after successful login."""
        if identifier in self.attempts:
            del self.attempts[identifier]
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """Get remaining login attempts."""
        if identifier not in self.attempts:
            return self.max_attempts
        
        count, first_attempt, locked_until = self.attempts[identifier]
        
        # If locked, no attempts
        if locked_until and time.time() < locked_until:
            return 0
        
        # If window expired, full attempts
        if time.time() - first_attempt > self.window_seconds:
            return self.max_attempts
        
        return max(0, self.max_attempts - count)


# Global brute force protector
_brute_force_protector = BruteForceProtection()


def check_login_attempt(identifier: str) -> tuple[bool, Optional[int]]:
    """Check login attempt against brute force protection."""
    return _brute_force_protector.check_login_attempt(identifier)


def reset_login_attempts(identifier: str) -> None:
    """Reset login attempts after successful login."""
    _brute_force_protector.reset_attempts(identifier)


def get_remaining_login_attempts(identifier: str) -> int:
    """Get remaining login attempts."""
    return _brute_force_protector.get_remaining_attempts(identifier)
