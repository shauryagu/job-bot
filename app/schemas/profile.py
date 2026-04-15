"""
Profile Schemas Module

Defines Pydantic schemas for profile-related API requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    """Profile response schema."""

    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    visa_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Profile update schema."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    visa_status: Optional[str] = None