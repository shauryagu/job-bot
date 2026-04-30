"""
Unit Tests for Company Models and Services

Tests the company data models and business logic.
"""

import pytest
from datetime import datetime
from app.models.company import Company, CompanyPriority, CompanyStatus, ATSType
from app.services.companies import CompanyService, SuggestionService
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.core.exceptions import ValidationException, NotFoundException


class TestCompanyModel:
    """Tests for Company model."""

    def test_company_creation(self):
        """Test creating a Company instance."""
        company = Company(
            name="Test Company",
            priority=CompanyPriority.PRIORITY_5,
            ats_type=ATSType.GREENHOUSE,
            careers_url="https://test.com/careers",
            locations='["New York", "Remote"]',
            notes="Test notes",
            status=CompanyStatus.ACTIVE,
        )

        assert company.name == "Test Company"
        assert company.priority == CompanyPriority.PRIORITY_5
        assert company.ats_type == ATSType.GREENHOUSE
        assert company.status == CompanyStatus.ACTIVE

    def test_company_priority_enum(self):
        """Test CompanyPriority enum values."""
        assert CompanyPriority.PRIORITY_1.value == 1
        assert CompanyPriority.PRIORITY_2.value == 2
        assert CompanyPriority.PRIORITY_3.value == 3
        assert CompanyPriority.PRIORITY_4.value == 4
        assert CompanyPriority.PRIORITY_5.value == 5

    def test_company_status_enum(self):
        """Test CompanyStatus enum values."""
        assert CompanyStatus.ACTIVE.value == "active"
        assert CompanyStatus.PAUSED.value == "paused"
        assert CompanyStatus.ARCHIVED.value == "archived"

    def test_ats_type_enum(self):
        """Test ATSType enum values."""
        assert ATSType.GREENHOUSE.value == "greenhouse"
        assert ATSType.LEVER.value == "lever"
        assert ATSType.ASHBY.value == "ashby"
        assert ATSType.WORKDAY.value == "workday"
        assert ATSType.MANUAL.value == "manual"
        assert ATSType.OTHER.value == "other"

    def test_company_string_representation(self):
        """Test string representation of Company."""
        company = Company(
            name="Test Company", priority=CompanyPriority.PRIORITY_5, ats_type=ATSType.GREENHOUSE
        )

        str_repr = str(company)
        assert "Test Company" in str_repr
        assert "5" in str_repr


class TestCompanyService:
    """Tests for CompanyService."""

    def test_create_company(self, db_session):
        """Test creating a company."""
        service = CompanyService(db_session)
        company_data = CompanyCreate(name="New Company", priority=CompanyPriority.PRIORITY_4, ats_type=ATSType.LEVER)

        company = service.create_company(company_data)

        assert company.name == "New Company"
        assert company.priority == CompanyPriority.PRIORITY_4
        assert company.ats_type == ATSType.LEVER
        assert company.status == CompanyStatus.ACTIVE

    def test_create_duplicate_company(self, db_session):
        """Test creating duplicate company raises error."""
        service = CompanyService(db_session)
        company_data = CompanyCreate(name="Duplicate Company")

        service.create_company(company_data)

        with pytest.raises(ValidationException, match="already exists"):
            service.create_company(company_data)

    def test_get_company(self, db_session):
        """Test getting a company by ID."""
        service = CompanyService(db_session)
        company = service.create_company(CompanyCreate(name="Test Company"))

        retrieved = service.get_company(company.id)

        assert retrieved.id == company.id
        assert retrieved.name == "Test Company"

    def test_get_nonexistent_company(self, db_session):
        """Test getting non-existent company raises error."""
        service = CompanyService(db_session)

        with pytest.raises(NotFoundException, match="not found"):
            service.get_company(99999)

    def test_get_company_by_name(self, db_session):
        """Test getting company by name."""
        service = CompanyService(db_session)
        service.create_company(CompanyCreate(name="Test Company"))

        company = service.get_company_by_name("Test Company")

        assert company is not None
        assert company.name == "Test Company"

    def test_get_company_by_name_not_found(self, db_session):
        """Test getting non-existent company by name."""
        service = CompanyService(db_session)

        company = service.get_company_by_name("Nonexistent Company")

        assert company is None

    def test_list_companies(self, db_session):
        """Test listing companies with filtering."""
        service = CompanyService(db_session)

        service.create_company(CompanyCreate(name="Company A", priority=CompanyPriority.PRIORITY_5))
        service.create_company(CompanyCreate(name="Company B", priority=CompanyPriority.PRIORITY_3))
        service.create_company(CompanyCreate(name="Company C", priority=CompanyPriority.PRIORITY_5))

        companies, total = service.list_companies()

        assert total == 3
        assert len(companies) == 3

    def test_list_companies_by_priority(self, db_session):
        """Test listing companies filtered by priority."""
        service = CompanyService(db_session)

        service.create_company(CompanyCreate(name="Company A", priority=CompanyPriority.PRIORITY_5))
        service.create_company(CompanyCreate(name="Company B", priority=CompanyPriority.PRIORITY_3))
        service.create_company(CompanyCreate(name="Company C", priority=CompanyPriority.PRIORITY_5))

        companies, total = service.list_companies(priority=CompanyPriority.PRIORITY_5)

        assert total == 2
        assert all(c.priority == CompanyPriority.PRIORITY_5 for c in companies)

    def test_list_companies_by_status(self, db_session):
        """Test listing companies filtered by status."""
        service = CompanyService(db_session)

        active = service.create_company(CompanyCreate(name="Active Company"))
        paused = service.create_company(CompanyCreate(name="Paused Company"))

        # Update status
        service.update_company(paused.id, CompanyUpdate(status=CompanyStatus.PAUSED))

        companies, total = service.list_companies(status=CompanyStatus.ACTIVE)

        assert total == 1
        assert companies[0].name == "Active Company"

    def test_list_companies_by_ats_type(self, db_session):
        """Test listing companies filtered by ATS type."""
        service = CompanyService(db_session)

        service.create_company(CompanyCreate(name="Greenhouse Company", ats_type=ATSType.GREENHOUSE))
        service.create_company(CompanyCreate(name="Lever Company", ats_type=ATSType.LEVER))

        companies, total = service.list_companies(ats_type=ATSType.GREENHOUSE)

        assert total == 1
        assert companies[0].ats_type == ATSType.GREENHOUSE

    def test_list_companies_pagination(self, db_session):
        """Test listing companies with pagination."""
        service = CompanyService(db_session)

        for i in range(5):
            service.create_company(CompanyCreate(name=f"Company {i}"))

        companies, total = service.list_companies(limit=2, offset=0)

        assert total == 5
        assert len(companies) == 2

    def test_update_company(self, db_session):
        """Test updating a company."""
        service = CompanyService(db_session)
        company = service.create_company(CompanyCreate(name="Original Name", priority=CompanyPriority.PRIORITY_3))

        update_data = CompanyUpdate(name="Updated Name", priority=CompanyPriority.PRIORITY_5)
        updated = service.update_company(company.id, update_data)

        assert updated.name == "Updated Name"
        assert updated.priority == CompanyPriority.PRIORITY_5

    def test_update_nonexistent_company(self, db_session):
        """Test updating non-existent company raises error."""
        service = CompanyService(db_session)

        with pytest.raises(NotFoundException, match="not found"):
            service.update_company(99999, CompanyUpdate(name="Test"))

    def test_delete_company(self, db_session):
        """Test deleting a company."""
        service = CompanyService(db_session)
        company = service.create_company(CompanyCreate(name="Test Company"))

        service.delete_company(company.id)

        with pytest.raises(NotFoundException, match="not found"):
            service.get_company(company.id)

    def test_delete_nonexistent_company(self, db_session):
        """Test deleting non-existent company raises error."""
        service = CompanyService(db_session)

        with pytest.raises(NotFoundException, match="not found"):
            service.delete_company(99999)

    def test_pause_company(self, db_session):
        """Test pausing a company."""
        service = CompanyService(db_session)
        company = service.create_company(CompanyCreate(name="Test Company", status=CompanyStatus.ACTIVE))

        paused = service.pause_company(company.id)

        assert paused.status == CompanyStatus.PAUSED

    def test_activate_company(self, db_session):
        """Test activating a company."""
        service = CompanyService(db_session)
        company = service.create_company(CompanyCreate(name="Test Company", status=CompanyStatus.PAUSED))

        activated = service.activate_company(company.id)

        assert activated.status == CompanyStatus.ACTIVE

    def test_get_companies_by_ats_type(self, db_session):
        """Test getting companies by ATS type."""
        service = CompanyService(db_session)

        service.create_company(CompanyCreate(name="Company A", ats_type=ATSType.GREENHOUSE))
        service.create_company(CompanyCreate(name="Company B", ats_type=ATSType.LEVER))
        service.create_company(CompanyCreate(name="Company C", ats_type=ATSType.GREENHOUSE))

        companies = service.get_companies_by_ats_type(ATSType.GREENHOUSE)

        assert len(companies) == 2
        assert all(c.ats_type == ATSType.GREENHOUSE for c in companies)

    def test_search_companies(self, db_session):
        """Test searching companies by name."""
        service = CompanyService(db_session)

        service.create_company(CompanyCreate(name="Tech Company"))
        service.create_company(CompanyCreate(name="Finance Company"))
        service.create_company(CompanyCreate(name="Tech Startup"))

        companies = service.search_companies("Tech")

        assert len(companies) == 2
        assert all("Tech" in c.name for c in companies)

    def test_search_companies_limit(self, db_session):
        """Test search with limit."""
        service = CompanyService(db_session)

        for i in range(10):
            service.create_company(CompanyCreate(name=f"Test Company {i}"))

        companies = service.search_companies("Test", limit=5)

        assert len(companies) == 5


class TestSuggestionService:
    """Tests for SuggestionService."""

    def test_suggest_companies_from_jobs(self, db_session):
        """Test suggesting companies from fetched jobs."""
        service = SuggestionService(db_session)

        fetched_jobs = [
            {
                "company": "New Company A",
                "url": "https://greenhouse.io/jobs/1",
                "priority_score": 85,
                "location": "New York",
            },
            {
                "company": "New Company A",
                "url": "https://greenhouse.io/jobs/2",
                "priority_score": 80,
                "location": "Remote",
            },
            {
                "company": "New Company B",
                "url": "https://lever.co/jobs/1",
                "priority_score": 75,
                "location": "Remote",
            },
        ]

        suggestions = service.suggest_companies_from_jobs(fetched_jobs)

        assert len(suggestions) == 2
        assert suggestions[0]["name"] == "New Company A"
        assert suggestions[0]["job_count"] == 2
        assert suggestions[0]["ats_type"] == ATSType.GREENHOUSE

    def test_suggest_companies_excludes_existing(self, db_session):
        """Test suggestions exclude existing companies."""
        service = SuggestionService(db_session)

        # Create existing company
        from app.services.companies import CompanyService

        company_service = CompanyService(db_session)
        company_service.create_company(CompanyCreate(name="Existing Company"))

        fetched_jobs = [
            {"company": "Existing Company", "url": "https://example.com/jobs/1", "priority_score": 85},
            {"company": "New Company", "url": "https://example.com/jobs/2", "priority_score": 75},
        ]

        suggestions = service.suggest_companies_from_jobs(fetched_jobs)

        assert len(suggestions) == 1
        assert suggestions[0]["name"] == "New Company"

    def test_detect_ats_type(self, db_session):
        """Test ATS type detection."""
        service = SuggestionService(db_session)

        assert service._detect_ats_type({"url": "https://greenhouse.io/jobs/1"}) == ATSType.GREENHOUSE
        assert service._detect_ats_type({"url": "https://lever.co/jobs/1"}) == ATSType.LEVER
        assert service._detect_ats_type({"url": "https://ashbyhq.com/jobs/1"}) == ATSType.ASHBY
        assert service._detect_ats_type({"url": "https://workday.com/jobs/1"}) == ATSType.WORKDAY
        assert service._detect_ats_type({"url": "https://example.com/jobs/1"}) == ATSType.OTHER

    def test_recommend_priority_high_quality(self, db_session):
        """Test priority recommendation for high quality jobs."""
        service = SuggestionService(db_session)

        stats = {"avg_priority_score": 85, "job_count": 5}
        assert service._recommend_priority(stats) == CompanyPriority.PRIORITY_5

    def test_recommend_priority_medium_quality(self, db_session):
        """Test priority recommendation for medium quality jobs."""
        service = SuggestionService(db_session)

        stats = {"avg_priority_score": 65, "job_count": 2}
        assert service._recommend_priority(stats) == CompanyPriority.PRIORITY_3

    def test_recommend_priority_low_quality(self, db_session):
        """Test priority recommendation for low quality jobs."""
        service = SuggestionService(db_session)

        stats = {"avg_priority_score": 45, "job_count": 1}
        assert service._recommend_priority(stats) == CompanyPriority.PRIORITY_1

    def test_suggest_companies_limit(self, db_session):
        """Test suggestion limit."""
        service = SuggestionService(db_session)

        fetched_jobs = [{"company": f"Company {i}", "url": "https://example.com/jobs/{i}", "priority_score": 70} for i in range(15)]

        suggestions = service.suggest_companies_from_jobs(fetched_jobs, limit=5)

        assert len(suggestions) == 5
