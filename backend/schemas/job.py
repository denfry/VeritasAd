from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

from ..models import JobStatus


class JobCreate(BaseModel):
    url: Optional[HttpUrl] = None
    platform: str
    input_type: str
    media_path: Optional[str] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: JobStatus
    platform: str
    input_type: str
    created_at: datetime
    updated_at: datetime
    result_path: Optional[str] = None
    result_url: Optional[str] = None
    media_path: Optional[str] = None
    media_url: Optional[str] = None
    error_message: Optional[str] = None

