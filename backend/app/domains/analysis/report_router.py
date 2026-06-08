"""Analysis domain - report generation and download."""
import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.dependencies import get_api_key
from app.core.errors import ValidationException
from app.models.database import get_db
from app.domains.analysis.service import AnalysisService
from app.domains.analysis.dependencies import get_analysis_service

router = APIRouter()
logger = structlog.get_logger(__name__)
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


@router.get("/{video_id}")
async def get_report(
    video_id: str,
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Download PDF report for a specific video analysis (generated on demand)."""
    try:
        if not VIDEO_ID_PATTERN.fullmatch(video_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid video_id format",
            )

        report_path = await service.get_or_generate_report(video_id=video_id, session=db)

        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Report file not found",
            )

        return FileResponse(
            path=str(report_path),
            media_type="application/pdf",
            filename=report_path.name,
        )

    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("report_retrieval_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve report: {str(e)}",
        )


@router.post("/{video_id}/generate")  # alias: POST /api/v1/report/{id}/generate
@router.post("/generate/{video_id}")
async def generate_report(
    video_id: str,
    api_key: str = Depends(get_api_key),
):
    """Generate a new PDF report for a video analysis."""
    try:
        raise HTTPException(
            status_code=400,
            detail="Report generation is automatic. Use the /analyze/check endpoint to analyze a video.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("report_generation_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}",
        )
