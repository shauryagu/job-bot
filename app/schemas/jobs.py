"""
Job Schemas Module

Defines Pydantic schemas for job-related API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.job import JobStatus, ActionBucket, LocationType


class JobResponse(BaseModel):
    """Job response schema."""

    id: int
    company: str
    role: str
    title_bucket: Optional[str] = None
    location_type: Optional[LocationType] = None
    priority_score: float = 0.0
    action_bucket: Optional[ActionBucket] = None
    status: JobStatus = JobStatus.NEW
    created_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response schema."""

    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobFetchRequest(BaseModel):
    """Job fetch request schema."""

    sources: List[str] = Field(default=["greenhouse", "lever", "ashby"])
    force_refresh: bool = Field(default=False)