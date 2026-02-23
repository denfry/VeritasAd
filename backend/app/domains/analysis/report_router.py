"""Analysis domain - report generation and download."""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import structlog

from app.core.dependencies import get_api_key

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/{video_id}")
async def get_report(
    video_id: str,
    api_key: str = Depends(get_api_key),
):
    """Download PDF report for a specific video analysis."""
    try:
        report_dir = Path("../data/reports")
        matching_reports = list(report_dir.glob(f"report_{video_id}_*.pdf"))

        if not matching_reports:
            raise HTTPException(
                status_code=404,
                detail=f"Report not found for video_id: {video_id}",
            )

        latest_report = max(matching_reports, key=lambda p: p.stat().st_mtime)

        if not latest_report.exists():
            raise HTTPException(
                status_code=404,
                detail="Report file not found",
            )

        return FileResponse(
            path=str(latest_report),
            media_type="application/pdf",
            filename=latest_report.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("report_retrieval_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve report: {str(e)}",
        )


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
