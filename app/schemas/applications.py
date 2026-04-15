"""
Application Schemas Module

Defines Pydantic schemas for application-related API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.application import ApplicationStage


class ApplicationResponse(BaseModel):
    """Application response schema."""

    id: int
    company: str
    role: str
    application_url: Optional[str] = None
    source: Optional[str] = None
    date_found: Optional[datetime] = None
    date_applied: Optional[datetime] = None
    resume_version: Optional[str] = None
    stage: ApplicationStage = ApplicationStage.APPLIED
    next_action: Optional[str] = None
    follow_up_due: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    """Application creation schema."""

    job_id: int
    company: str
    role: str
    resume_version: Optional[str] = None
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    """Application status update schema."""

    stage: ApplicationStage
    next_action: Optional[str] = None
    follow_up_due: Optional[datetime] = None