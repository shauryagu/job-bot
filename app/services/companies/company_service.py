"""
Company Service Module

Provides business logic for company management operations.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.company import Company, CompanyPriority, CompanyStatus, ATSType
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.core.logging import get_logger
from app.core.exceptions import ValidationException, NotFoundException


class CompanyService:
    """Service for company management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company."""
        existing = self.get_company_by_name(company_data.name)
        if existing:
            raise ValidationException(f"Company '{company_data.name}' already exists")

        company = Company(**company_data.model_dump())
        # Handle locations conversion
        if company_data.locations:
            company.locations_list = company_data.locations

        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)

        self.logger.info(f"Created company: {company.name}")
        return company

    def get_company(self, company_id: int) -> Company:
        """Get company by ID."""
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFoundException(f"Company with ID {company_id} not found")
        return company

    def get_company_by_name(self, name: str) -> Optional[Company]:
        """Get company by name."""
        return self.db.query(Company).filter(Company.name == name).first()

    def list_companies(
        self,
        status: Optional[CompanyStatus] = None,
        ats_type: Optional[ATSType] = None,
        priority: Optional[CompanyPriority] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Company], int]:
        """List companies with filtering."""
        query = self.db.query(Company)

        if status:
            query = query.filter(Company.status == status)
        if ats_type:
            query = query.filter(Company.ats_type == ats_type)
        if priority:
            query = query.filter(Company.priority == priority)

        total = query.count()
        companies = query.order_by(Company.priority.desc(), Company.name).offset(offset).limit(limit).all()

        return companies, total

    def update_company(self, company_id: int, update_data: CompanyUpdate) -> Company:
        """Update company details."""
        company = self.get_company(company_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if field == "locations" and value is not None:
                company.locations_list = value
            else:
                setattr(company, field, value)

        self.db.commit()
        self.db.refresh(company)

        self.logger.info(f"Updated company: {company.name}")
        return company

    def delete_company(self, company_id: int) -> None:
        """Delete company."""
        company = self.get_company(company_id)

        if company.jobs:
            raise ValidationException(
                f"Cannot delete company '{company.name}' with {len(company.jobs)} associated jobs"
            )

        self.db.delete(company)
        self.db.commit()

        self.logger.info(f"Deleted company: {company.name}")

    def pause_company(self, company_id: int) -> Company:
        """Pause company (stop fetching)."""
        company = self.get_company(company_id)
        company.status = CompanyStatus.PAUSED
        self.db.commit()
        self.db.refresh(company)

        self.logger.info(f"Paused company: {company.name}")
        return company

    def activate_company(self, company_id: int) -> Company:
        """Reactivate company."""
        company = self.get_company(company_id)
        company.status = CompanyStatus.ACTIVE
        self.db.commit()
        self.db.refresh(company)

        self.logger.info(f"Activated company: {company.name}")
        return company

    def get_companies_by_ats_type(self, ats_type: ATSType) -> List[Company]:
        """Get all companies by ATS type."""
        return (
            self.db.query(Company)
            .filter(Company.ats_type == ats_type, Company.status == CompanyStatus.ACTIVE)
            .all()
        )

    def search_companies(self, query: str, limit: int = 10) -> List[Company]:
        """Search companies by name."""
        return (
            self.db.query(Company)
            .filter(Company.name.ilike(f"%{query}%"), Company.status != CompanyStatus.ARCHIVED)
            .limit(limit)
            .all()
        )
