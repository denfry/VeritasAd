from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.core.dependencies import get_api_key
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()
report_gen = ReportGenerator()


@router.get("/{video_id}")
async def get_report(
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Download PDF report for a specific video analysis

    Args:
        video_id: Video ID from analysis
        api_key: User API key

    Returns:
        PDF file download
    """
    try:
        # Find report file
        report_dir = Path("../data/reports")

        # Search for report with this video_id
        matching_reports = list(report_dir.glob(f"report_{video_id}_*.pdf"))

        if not matching_reports:
            raise HTTPException(
                status_code=404,
                detail=f"Report not found for video_id: {video_id}"
            )

        # Get the most recent report
        latest_report = max(matching_reports, key=lambda p: p.stat().st_mtime)

        if not latest_report.exists():
            raise HTTPException(
                status_code=404,
                detail="Report file not found"
            )

        return FileResponse(
            path=str(latest_report),
            media_type="application/pdf",
            filename=latest_report.name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve report: {str(e)}"
        )


@router.post("/generate/{video_id}")
async def generate_report(
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Generate a new PDF report for a video analysis

    Args:
        video_id: Video ID from analysis
        api_key: User API key

    Returns:
        Report generation status and file path
    """
    try:
        # In a real implementation, you would:
        # 1. Fetch analysis data from database
        # 2. Generate report using ReportGenerator
        # For now, return an error asking to use the analyze endpoint

        raise HTTPException(
            status_code=400,
            detail="Report generation is automatic. Use the /analyze/check endpoint to analyze a video."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )
