"""API v1 router - aggregates domain routers."""
from fastapi import APIRouter

from app.domains.users import router as users_router
from app.domains.admin import router as admin_router
from app.domains.payment import router as payment_router
from app.domains.analysis import router as analysis_router
from app.domains.upload import router as upload_router
from app.domains.health import router as health_router
from app.domains.security import router as security_router
from app.api.v1 import telegram as telegram_router
from app.api.v1.brands import router as brands_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(analysis_router, tags=["analysis"])
api_router.include_router(payment_router, prefix="/payment", tags=["payment"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
api_router.include_router(brands_router, tags=["brands"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(telegram_router.router, prefix="/telegram", tags=["telegram"])
