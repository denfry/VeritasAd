"""VeritasAd API - Application factory and entry point."""
from contextlib import asynccontextmanager
from typing import cast

from app.core.observability import init_sentry, init_opentelemetry

# Initialize Sentry early (before other imports that might throw)
init_sentry()
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from slowapi.errors import RateLimitExceeded
import structlog
from sqlalchemy import text

from app.core.config import settings
from app.core.errors import (
    VeritasAdException,
    general_exception_handler,
)
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    LoggingMiddleware,
)
from app.middleware.rate_limit import limiter
from app.models.database import init_db, close_db, engine
from app.core.redis import redis_client
from app.utils.logger import setup_logging
from app.api.v1.router import api_router

setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(
        "app_startup",
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )

    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        raise

    try:
        await redis_client.connect()
        logger.info("redis_connected")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        if settings.ENVIRONMENT == "production":
            raise

    logger.info("app_ready")

    yield

    logger.info("app_shutdown_started")

    try:
        await close_db()
        logger.info("database_closed")
    except Exception as e:
        logger.error("database_close_failed", error=str(e))

    try:
        await redis_client.close()
        logger.info("redis_closed")
    except Exception as e:
        logger.error("redis_close_failed", error=str(e))

    logger.info("app_shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application (application factory pattern)."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-powered advertising detection system for video content",
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG,
    )

    # Middleware (order matters)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS,
        )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # CSRF Protection - enabled in production (if available)
    # Note: FastAPI/Starlette may not have CSRF middleware built-in
    # For production, consider using custom CSRF protection or API tokens
    # if settings.ENVIRONMENT == "production":
    #     try:
    #         from starlette.middleware.csrf import CSRFProtectMiddleware
    #         app.add_middleware(CSRFProtectMiddleware)
    #     except ImportError:
    #         logger.warning("CSRF middleware not available, using token-based protection")
    
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.state.limiter = limiter

    # Exception handlers
    async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
        if not isinstance(exc, RateLimitExceeded):
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error during rate limit handling"},
            )
        detail = str(exc)
        retry_after = getattr(exc, "retry_after", 60)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too Many Requests",
                "error": "rate_limit_exceeded",
                "message": detail or "Rate limit exceeded. Try again later.",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    async def veritasad_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        exc = cast(VeritasAdException, exc)
        status_code = getattr(exc, "status_code", 422)
        message = getattr(exc, "message", str(exc))
        detail = getattr(exc, "detail", None)
        content = {"error": "veritasad_error", "message": message}
        if detail:
            content["detail"] = detail
        return JSONResponse(status_code=status_code, content=content)

    async def validation_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        if not isinstance(exc, RequestValidationError):
            return JSONResponse(
                status_code=500,
                content={"detail": "Unexpected error during validation handling"},
            )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Request validation failed",
                "errors": exc.errors(),
                "message": "Check your input data",
            },
        )

    async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        if not isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=500,
                content={"detail": "Unexpected error in HTTP exception handler"},
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "error_type": "http_error",
            },
            headers=exc.headers if exc.headers else None,
        )

    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_exception_handler(VeritasAdException, veritasad_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Root endpoints
    @app.get("/")
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "running",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "api": settings.API_V1_STR,
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }

    @app.get("/ready")
    async def readiness_check():
        checks = {"database": False, "redis": False}
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception:
            pass
        try:
            if redis_client.client is not None:
                await redis_client.client.ping()
            checks["redis"] = True
        except Exception:
            checks["redis"] = False
        all_ready = all(checks.values())
        return {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
        }

    return app


app = create_app()
init_opentelemetry(app)
