from fastapi import APIRouter
from app.api.v1 import upload, analyze, health, report

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(health.router, tags=["health"])