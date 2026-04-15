"""
Tracker Models Module

Defines database models for tracker-related data.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from app.db.base import BaseModel
import datetime


class TrackerEntry(BaseModel):
    """
    Tracker entry model.

    Stores comprehensive tracking data for job applications.
    """

    __tablename__ = "tracker_entries"

    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    company = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    title_bucket = Column(String)
    location = Column(String)
    source = Column(String)
    date_posted = Column(DateTime)
    priority_score = Column(Integer)
    resume_version = Column(String)
    date_applied = Column(DateTime)
    referral_target = Column(String)
    contact_name = Column(String)
    contact_type = Column(String)
    outreach_goal = Column(Text)
    outreach_sent = Column(DateTime)
    response = Column(Text)
    stage = Column(String)
    next_action = Column(Text)
    last_touched = Column(DateTime, default=datetime.datetime.utcnow)
    follow_up_due = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<TrackerEntry(id={self.id}, company={self.company}, role={self.role}, stage={self.stage})>"