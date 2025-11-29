from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VideoUploadResponse(BaseModel):
    """Response after video upload"""
    video_id: str
    status: str
    source: str  # file or url
    message: str
    file_path: Optional[str] = None


class VideoMetadata(BaseModel):
    """Video file metadata"""
    video_id: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    file_size: int
    created_at: datetime


class FrameAnalysis(BaseModel):
    """Single frame analysis result"""
    frame_number: int
    timestamp: float
    has_logo: bool
    detected_brands: list[str] = []
    confidence: float
