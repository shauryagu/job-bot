"""
Company Schemas Module

Defines Pydantic schemas for company-related API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from app.models.company import CompanyPriority, CompanyStatus, ATSType


class CompanyResponse(BaseModel):
    """Company response schema."""

    id: int
    name: str
    priority: CompanyPriority
    ats_type: ATSType
    careers_url: Optional[str] = None
    locations: Optional[List[str]] = None
    notes: Optional[str] = None
    status: CompanyStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: Any) -> "CompanyResponse":
        """Create response from ORM object with locations conversion."""
        data = {
            "id": obj.id,
            "name": obj.name,
            "priority": obj.priority,
            "ats_type": obj.ats_type,
            "careers_url": obj.careers_url,
            "locations": obj.locations_list if hasattr(obj, "locations_list") else None,
            "notes": obj.notes,
            "status": obj.status,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    """Company creation schema."""

    name: str = Field(..., min_length=1, max_length=200)
    priority: CompanyPriority = CompanyPriority.PRIORITY_3
    ats_type: ATSType = ATSType.OTHER
    careers_url: Optional[str] = None
    locations: Optional[List[str]] = None
    notes: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Company update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    priority: Optional[CompanyPriority] = None
    ats_type: Optional[ATSType] = None
    careers_url: Optional[str] = None
    locations: Optional[List[str]] = None
    notes: Optional[str] = None
    status: Optional[CompanyStatus] = None


class CompanyListResponse(BaseModel):
    """Company list response schema."""

    companies: List[CompanyResponse]
    total: int
    limit: int
    offset: int


class CompanyFetchRequest(BaseModel):
    """Company-specific job fetch request schema."""

    company_ids: List[int] = Field(default=[])
    ats_types: Optional[List[ATSType]] = None
    force_refresh: bool = Field(default=False)
