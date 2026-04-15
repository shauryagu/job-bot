"""
Job Models Module

Defines database models for job-related data.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import BaseModel
import datetime


class JobStatus(str, Enum):
    """Job status enumeration."""

    NEW = "new"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ARCHIVED = "archived"


class JobSource(str, Enum):
    """Job source enumeration."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    MANUAL = "manual"
    OTHER = "other"


class LocationType(str, Enum):
    """Location type enumeration."""

    NYC = "nyc"
    REMOTE = "remote"
    HYBRID = "hybrid"
    OTHER = "other"


class ActionBucket(str, Enum):
    """Action bucket enumeration."""

    APPLY_NOW = "apply_now"
    APPLY_SOON = "apply_soon"
    OUTREACH_FIRST = "outreach_first"
    MONITOR = "monitor"
    SKIP = "skip"


class JobRaw(BaseModel):
    """
    Raw job data model.

    Stores unprocessed job data from various sources.
    """

    __tablename__ = "jobs_raw"

    source = Column(String, nullable=False, index=True)
    source_job_id = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    location_raw = Column(String)
    description_raw = Column(Text)
    url = Column(String, nullable=False)
    date_posted_raw = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    ats_type = Column(String)
    metadata_json = Column(Text)  # JSON string for additional metadata

    # Relationship to normalized job
    normalized_jobs = relationship("JobNormalized", back_populates="raw_job")

    def __repr__(self):
        return f"<JobRaw(id={self.id}, company={self.company}, title={self.title})>"


class JobNormalized(BaseModel):
    """
    Normalized job data model.

    Stores processed and normalized job data.
    """

    __tablename__ = "jobs_normalized"

    raw_job_id = Column(Integer, ForeignKey("jobs_raw.id"), nullable=True)
    company = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    title_bucket = Column(String)
    location_type = Column(SQLEnum(LocationType))
    ny_match = Column(Integer, default=0)
    remote_match = Column(Integer, default=0)

    # Scoring fields
    fit_score = Column(Integer, default=0)
    company_priority = Column(Integer, default=0)
    freshness_score = Column(Integer, default=0)
    location_score = Column(Integer, default=0)
    referral_score = Column(Integer, default=0)
    effort_penalty = Column(Integer, default=0)
    priority_score = Column(Float, default=0.0)

    action_bucket = Column(SQLEnum(ActionBucket))
    status = Column(SQLEnum(JobStatus), default=JobStatus.NEW, index=True)
    duplicate_group_id = Column(String, index=True)

    # Relationship to raw job
    raw_job = relationship("JobRaw", back_populates="normalized_jobs")

    def __repr__(self):
        return f"<JobNormalized(id={self.id}, company={self.company}, role={self.role}, score={self.priority_score})>"