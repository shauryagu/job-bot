"""
Outreach Schemas Module

Defines Pydantic schemas for outreach-related API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.contact import ContactType


class OutreachResponse(BaseModel):
    """Outreach response schema."""

    id: int
    application_id: Optional[int] = None
    contact_id: Optional[int] = None
    outreach_goal: Optional[str] = None
    draft_text: Optional[str] = None
    sent_at: Optional[datetime] = None
    follow_up_due: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OutreachDraftRequest(BaseModel):
    """Outreach draft generation request schema."""

    application_id: int
    contact_id: int
    contact_type: ContactType