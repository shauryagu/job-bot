"""
Outreach Models Module

Defines database models for outreach-related data.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import BaseModel
import datetime


class OutreachStatus(str, Enum):
    """Outreach status enumeration."""

    DRAFT = "draft"
    SENT = "sent"
    REPLIED = "replied"
    IGNORED = "ignored"
    FAILED = "failed"


class Outreach(BaseModel):
    """
    Outreach model.

    Stores outreach message data and tracking.
    """

    __tablename__ = "outreach"

    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    outreach_goal = Column(Text)
    draft_text = Column(Text)
    sent_at = Column(DateTime)
    response_status = Column(SQLEnum(OutreachStatus), default=OutreachStatus.DRAFT)
    follow_up_due = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<Outreach(id={self.id}, status={self.response_status}, sent_at={self.sent_at})>"