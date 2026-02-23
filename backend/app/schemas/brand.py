from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.models.database import BrandCategory


class BrandBase(BaseModel):
    """Base brand schema"""
    name: str = Field(..., description="Brand name", min_length=1, max_length=255)
    category: BrandCategory = Field(default=BrandCategory.OTHER, description="Brand category")
    description: Optional[str] = Field(None, description="Brand description")
    aliases: Optional[List[str]] = Field(None, description="Brand name aliases/variations")
    detection_threshold: float = Field(default=0.15, ge=0.0, le=1.0, description="Detection threshold")


class BrandCreate(BrandBase):
    """Schema for creating a new brand"""
    logo_url: Optional[str] = Field(None, description="URL to brand logo")
    # Note: logo_base64 would be added if needed for direct upload


class BrandUpdate(BaseModel):
    """Schema for updating a brand"""
    name: Optional[str] = Field(None, description="Brand name", min_length=1, max_length=255)
    category: Optional[BrandCategory] = Field(None, description="Brand category")
    description: Optional[str] = Field(None, description="Brand description")
    aliases: Optional[List[str]] = Field(None, description="Brand name aliases/variations")
    logo_url: Optional[str] = Field(None, description="URL to brand logo")
    logo_base64: Optional[str] = Field(None, description="Base64 encoded logo image")
    is_active: Optional[bool] = Field(None, description="Whether brand is active")
    detection_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Detection threshold")


class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: int
    user_id: Optional[int] = None
    logo_url: Optional[str] = None
    is_active: bool
    brand_metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandListResponse(BaseModel):
    """Schema for list of brands"""
    items: List[BrandResponse]
    total: int
    page: int
    page_size: int


class BrandDetection(BaseModel):
    """Detected brand in analysis"""
    name: str
    confidence: float
    timestamps: List[float] = []
    source: Optional[str] = Field("known", description="Detection source: known, zero_shot, ocr")
    occurrences: Optional[int] = Field(1, description="Number of occurrences")


class BrandCategoryResponse(BaseModel):
    """Brand category info"""
    value: str
    label: str
    count: Optional[int] = None
