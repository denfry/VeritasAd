from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for video analysis"""
    url: Optional[str] = Field(None, description="Video URL (YouTube, Telegram, etc)")
    platform: Optional[str] = Field(None, description="Platform: telegram, youtube, vk, instagram, tiktok")


class BrandDetection(BaseModel):
    """Detected brand information"""
    name: str
    confidence: float
    timestamps: List[float] = []


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    video_id: str
    has_advertising: bool
    confidence_score: float

    # Detailed scores
    visual_score: float
    audio_score: float
    text_score: float
    disclosure_score: float

    # Detections
    detected_brands: List[BrandDetection] = []
    detected_keywords: List[str] = []
    transcript: Optional[str] = None
    disclosure_text: Optional[str] = None

    # Metadata
    status: str
    processing_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisCreate(BaseModel):
    """Create new analysis record"""
    video_id: str
    user_api_key: str
    source_url: Optional[str] = None
    source_type: Optional[str] = None


class AnalysisUpdate(BaseModel):
    """Update analysis with results"""
    status: Optional[str] = None
    has_advertising: Optional[bool] = None
    confidence_score: Optional[float] = None
    visual_score: Optional[float] = None
    audio_score: Optional[float] = None
    text_score: Optional[float] = None
    disclosure_score: Optional[float] = None
    detected_brands: Optional[dict] = None
    detected_keywords: Optional[List[str]] = None
    transcript: Optional[str] = None
    disclosure_text: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    report_path: Optional[str] = None
    completed_at: Optional[datetime] = None


class QuickAnalysisResponse(BaseModel):
    """Quick response for analysis endpoint"""
    video_id: str
    status: str
    message: str
