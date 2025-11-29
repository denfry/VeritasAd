from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    email: Optional[EmailStr] = None
    plan: str = Field(default="free", description="User plan: free, pro, enterprise")


class UserCreate(UserBase):
    """Create new user"""
    pass


class UserResponse(UserBase):
    """User response model"""
    id: int
    api_key: str
    limit: int
    used: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    """User usage statistics"""
    plan: str
    limit: int
    used: int
    remaining: int
    reset_date: Optional[datetime] = None
