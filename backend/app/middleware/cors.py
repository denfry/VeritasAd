"""Custom CORS middleware with regex origin support and credentials."""

import re
from typing import Callable, List, Optional, Pattern

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.types import ASGIApp


class CORSMiddlewareRegex(BaseHTTPMiddleware):
    """
    CORS middleware that supports regex patterns for origins.
    Works correctly with allow_credentials=True.
    """

    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str],
        allow_origin_regex: Optional[str] = None,
        allow_credentials: bool = True,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
    ) -> None:
        super().__init__(app)
        self.allow_origins = allow_origins or []
        self.allow_credentials = allow_credentials
        self.allow_methods = [
            m.upper()
            for m in (allow_methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
        ]
        self.allow_headers = [h.lower() for h in (allow_headers or ["*"])]
        self.expose_headers = expose_headers or []

        # Compile regex pattern if provided
        self.allow_origin_regex: Optional[Pattern[str]] = None
        if allow_origin_regex:
            self.allow_origin_regex = re.compile(allow_origin_regex)

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed via exact match or regex."""
        if origin in self.allow_origins:
            return True
        if self.allow_origin_regex and self.allow_origin_regex.fullmatch(origin):
            return True
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin")

        # If no origin header, not a CORS request
        if not origin:
            return await call_next(request)

        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            return await call_next(request)

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = PlainTextResponse("OK", status_code=200)
            response.headers["access-control-allow-origin"] = origin
            response.headers["access-control-allow-methods"] = ", ".join(self.allow_methods)
            response.headers["access-control-allow-headers"] = "*"
            response.headers["access-control-max-age"] = "600"

            if self.allow_credentials:
                response.headers["access-control-allow-credentials"] = "true"

            return response

        # Regular request - add CORS headers to response
        response = await call_next(request)
        response.headers["access-control-allow-origin"] = origin

        if self.allow_credentials:
            response.headers["access-control-allow-credentials"] = "true"

        if self.expose_headers:
            response.headers["access-control-expose-headers"] = ", ".join(self.expose_headers)

        return response
