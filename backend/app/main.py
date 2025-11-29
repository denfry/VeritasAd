from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from slowapi.errors import RateLimitExceeded
import structlog

from app.core.config import settings
from app.core.errors import (
    VeritasAdException,
    veritasad_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    LoggingMiddleware,
)
from app.middleware.rate_limit import limiter, _rate_limit_exceeded_handler
from app.models.database import init_db, close_db
from app.core.redis import redis_client
from app.utils.logger import setup_logging
from app.api.v1.router import api_router

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(
        "app_startup",
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize database
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        raise

    # Initialize Redis
    try:
        await redis_client.connect()
        logger.info("redis_connected")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        # Continue without Redis for development
        if settings.ENVIRONMENT == "production":
            raise

    logger.info("app_ready")

    yield

    # Shutdown
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


# Create FastAPI application
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

# ==================== MIDDLEWARE ====================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# Trusted hosts
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS,
    )

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==================== EXCEPTION HANDLERS ====================

app.add_exception_handler(VeritasAdException, veritasad_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ==================== ROUTERS ====================

app.include_router(api_router, prefix=settings.API_V1_STR)

# ==================== ROOT ENDPOINTS ====================


@app.get("/")
async def root():
    """Root endpoint with API information"""
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
    """
    Health check endpoint for monitoring.
    Returns 200 if service is running.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/load balancers.
    Checks if all dependencies are ready.
    """
    checks = {"database": False, "redis": False}

    # Check database
    try:
        from app.models.database import engine

        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass

    # Check Redis
    try:
        if redis_client.client:
            await redis_client.client.ping()
            checks["redis"] = True
    except Exception:
        pass

    all_ready = all(checks.values())

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }