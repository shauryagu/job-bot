"""
Contact Models Module

Defines database models for contact-related data.
"""

from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum
from enum import Enum
from app.db.base import BaseModel


class ContactType(str, Enum):
    """Contact type enumeration."""

    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    ENGINEER = "engineer"
    ALUMN = "alumnus"
    FOUNDER = "founder"
    OTHER = "other"


class RelationshipStrength(str, Enum):
    """Relationship strength enumeration."""

    WARM = "warm"
    COLD = "cold"
    NONE = "none"


class Contact(BaseModel):
    """
    Contact model.

    Stores contact information for outreach purposes.
    """

    __tablename__ = "contacts"

    company = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String)
    contact_type = Column(SQLEnum(ContactType), index=True)
    profile_url = Column(String)
    relationship_strength = Column(SQLEnum(RelationshipStrength), default=RelationshipStrength.COLD)
    notes = Column(Text)

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name}, company={self.company}, type={self.contact_type})>"