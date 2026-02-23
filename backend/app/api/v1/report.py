from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import re

from app.core.dependencies import get_api_key
from app.core.config import settings
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
        # Validate video_id format - only alphanumeric, underscore, dash allowed
        # This prevents path traversal and command injection
        if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid video_id format. Only alphanumeric characters, underscores, and hyphens are allowed."
            )
        
        # Use absolute path from settings and resolve any symlinks
        report_dir = settings.reports_path.resolve()
        
        # Ensure report directory exists
        if not report_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="Reports directory not found"
            )
        
        # Search for report with this video_id
        matching_reports = []
        for report_file in report_dir.glob("report_*.pdf"):
            # Check if video_id is in filename
            if f"report_{video_id}_" in report_file.name:
                # Verify file is within report_dir (prevent symlink attacks)
                try:
                    resolved = report_file.resolve()
                    # Ensure the resolved path is still within report_dir
                    if str(resolved).startswith(str(report_dir)):
                        matching_reports.append(report_file)
                except Exception:
                    # Skip files that can't be resolved
                    continue

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
            filename=f"report_{video_id}.pdf",
            # Prevent caching of sensitive reports
            headers={"Cache-Control": "private, no-store"}
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
        # Validate video_id format
        if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid video_id format"
            )
        
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
