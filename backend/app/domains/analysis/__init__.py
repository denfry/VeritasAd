"""Analysis domain - video analysis, progress streaming, and reports."""
from fastapi import APIRouter

from app.domains.analysis.analyze_router import router as analyze_router
from app.domains.analysis.progress_router import router as progress_router
from app.domains.analysis.report_router import router as report_router

router = APIRouter()
router.include_router(analyze_router, prefix="/analyze", tags=["analysis"])
router.include_router(progress_router, tags=["progress"])
router.include_router(report_router, prefix="/report", tags=["report"])
