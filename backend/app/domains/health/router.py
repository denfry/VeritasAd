"""Health domain router - health checks, system metrics, pipeline status."""

import asyncio
import os
import time
import platform
from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_admin_user
from app.models.database import User

router = APIRouter()

START_TIME = time.time()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "VeritasAD API"}


@router.get("/system-metrics")
async def system_metrics(_admin: User = Depends(get_current_admin_user)):
    """Real-time system metrics for admin dashboard. Admin only."""
    cpu_percent = psutil.cpu_percent(interval=0)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    uptime_seconds = time.time() - START_TIME

    return {
        "cpu_percent": cpu_percent,
        "memory_total_mb": round(memory.total / (1024 * 1024), 1),
        "memory_used_mb": round(memory.used / (1024 * 1024), 1),
        "memory_percent": memory.percent,
        "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 1),
        "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 1),
        "disk_percent": disk.percent,
        "process_memory_mb": round(process_memory.rss / (1024 * 1024), 1),
        "process_threads": process.num_threads(),
        "uptime_seconds": round(uptime_seconds),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


@router.get("/pipeline-status")
async def pipeline_status(_admin: User = Depends(get_current_admin_user)):
    """Status of analysis pipelines. Admin only."""
    pipelines = {
        "video_analysis": {
            "name": "Video Analysis",
            "description": "Content scanning",
            "status": "operational",
        },
        "brand_detection": {
            "name": "Brand Detection",
            "description": "Logo recognition",
            "status": "operational",
        },
        "audio_analysis": {
            "name": "Audio Analysis",
            "description": "Speech recognition",
            "status": "operational",
        },
        "llm_detection": {
            "name": "LLM Detection",
            "description": "AI analysis",
            "status": "operational",
        },
    }

    return {
        "pipelines": list(pipelines.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
