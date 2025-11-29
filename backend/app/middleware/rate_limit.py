from typing import Callable
from fastapi import Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings


def get_api_key_or_ip(request: Request) -> str:
    """Get API key from header or fallback to IP address"""
    api_key = request.headers.get(settings.API_KEY_HEADER)
    if api_key:
        return f"key:{api_key}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=get_api_key_or_ip,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=settings.REDIS_URL,
)


class RateLimitMiddleware:
    """Rate limiting middleware using slowapi"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # slowapi handles rate limiting via decorators
        # This is just a placeholder for custom logic if needed
        response = await call_next(request)
        return response
