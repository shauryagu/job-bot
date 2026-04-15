"""
Application Models Module

Defines database models for application-related data.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import BaseModel
import datetime


class ApplicationStage(str, Enum):
    """Application stage enumeration."""

    APPLIED = "applied"
    SCREENING = "screening"
    TECHNICAL = "technical"
    ONSITE = "onsite"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(BaseModel):
    """
    Application model.

    Stores job application data and tracking information.
    """

    __tablename__ = "applications"

    normalized_job_id = Column(Integer, ForeignKey("jobs_normalized.id"), nullable=True)
    company = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    application_url = Column(String)
    source = Column(String)
    date_found = Column(DateTime)
    date_applied = Column(DateTime)
    resume_version = Column(String)
    stage = Column(SQLEnum(ApplicationStage), default=ApplicationStage.APPLIED, index=True)
    next_action = Column(Text)
    last_touched = Column(DateTime, default=datetime.datetime.utcnow)
    follow_up_due = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<Application(id={self.id}, company={self.company}, role={self.role}, stage={self.stage})>"