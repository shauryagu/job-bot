"""
Companies API Router

Handles company-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.company import CompanyStatus, ATSType
from app.schemas.company import (
    CompanyResponse,
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
)
from app.services.companies import CompanyService
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=CompanyListResponse)
async def get_companies(
    status: Optional[CompanyStatus] = None,
    ats_type: Optional[ATSType] = None,
    priority: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get all companies with optional filtering."""
    try:
        service = CompanyService(db)
        companies, total = service.list_companies(
            status=status, ats_type=ats_type, priority=priority, limit=limit, offset=offset
        )

        return CompanyListResponse(companies=companies, total=total, limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Failed to get companies: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get specific company details."""
    try:
        service = CompanyService(db)
        company = service.get_company(company_id)
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company {company_id}: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/", response_model=CompanyResponse)
async def create_company(company_data: CompanyCreate, db: Session = Depends(get_db)):
    """Create new company."""
    try:
        service = CompanyService(db)
        company = service.create_company(company_data)
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create company: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, update_data: CompanyUpdate, db: Session = Depends(get_db)):
    """Update company details."""
    try:
        service = CompanyService(db)
        company = service.update_company(company_id, update_data)
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update company {company_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.delete("/{company_id}")
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete company."""
    try:
        service = CompanyService(db)
        service.delete_company(company_id)
        return {"message": "Company deleted successfully", "company_id": company_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete company {company_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/{company_id}/pause", response_model=CompanyResponse)
async def pause_company(company_id: int, db: Session = Depends(get_db)):
    """Pause company (stop fetching)."""
    try:
        service = CompanyService(db)
        company = service.pause_company(company_id)
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause company {company_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/{company_id}/activate", response_model=CompanyResponse)
async def activate_company(company_id: int, db: Session = Depends(get_db)):
    """Reactivate company."""
    try:
        service = CompanyService(db)
        company = service.activate_company(company_id)
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate company {company_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.get("/by-ats/{ats_type}", response_model=List[CompanyResponse])
async def get_companies_by_ats(ats_type: ATSType, db: Session = Depends(get_db)):
    """Get companies by ATS type."""
    try:
        service = CompanyService(db)
        companies = service.get_companies_by_ats_type(ats_type)
        return companies
    except Exception as e:
        logger.error(f"Failed to get companies by ATS type {ats_type}: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.get("/search/{query}", response_model=List[CompanyResponse])
async def search_companies(query: str, db: Session = Depends(get_db)):
    """Search companies by name."""
    try:
        service = CompanyService(db)
        companies = service.search_companies(query)
        return companies
    except Exception as e:
        logger.error(f"Failed to search companies: {e}")
        raise DatabaseException(f"Database error: {str(e)}")
