"""
Company Models Module

Defines database models for company-related data.
"""

from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import BaseModel
import json


class CompanyPriority(int, Enum):
    """Company priority levels (1-5)."""

    PRIORITY_1 = 1  # Low priority
    PRIORITY_2 = 2  # Backup
    PRIORITY_3 = 3  # Moderate
    PRIORITY_4 = 4  # Strong target
    PRIORITY_5 = 5  # Top target


class CompanyStatus(str, Enum):
    """Company status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ATSType(str, Enum):
    """ATS type enumeration."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    MANUAL = "manual"
    OTHER = "other"


class Company(BaseModel):
    """
    Company watchlist model.

    Stores target companies with priority levels and ATS information.
    """

    __tablename__ = "companies"

    name = Column(String, nullable=False, index=True)
    priority = Column(SQLEnum(CompanyPriority), nullable=False, default=CompanyPriority.PRIORITY_3)
    ats_type = Column(SQLEnum(ATSType), nullable=False, default=ATSType.OTHER)
    careers_url = Column(String, nullable=True)
    locations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(CompanyStatus), default=CompanyStatus.ACTIVE, index=True)

    jobs = relationship("JobNormalized", back_populates="company_record")

    @property
    def locations_list(self) -> list:
        """Get locations as a list."""
        if self.locations:
            try:
                return json.loads(self.locations)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @locations_list.setter
    def locations_list(self, value: list):
        """Set locations from a list."""
        self.locations = json.dumps(value) if value else None

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, priority={self.priority.value})>"
