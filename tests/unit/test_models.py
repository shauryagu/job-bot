"""
Unit Tests for Data Models

Tests the data models and their validation.
"""

import pytest
from datetime import datetime
from app.models.job import JobRaw, JobNormalized, JobStatus
from app.models.application import Application, ApplicationStage
from app.models.contact import Contact
from app.models.outreach import Outreach
from app.models.profile import UserProfile
from app.models.tracker import TrackerEntry


class TestJobRaw:
    """Tests for JobRaw model."""

    def test_job_raw_creation(self):
        """Test creating a JobRaw instance."""
        job_raw = JobRaw(
            source="greenhouse",
            source_job_id="12345",
            company="Test Company",
            title="Software Engineer",
            url="https://example.com/jobs/12345",
            fetched_at=datetime.utcnow(),
        )

        assert job_raw.source == "greenhouse"
        assert job_raw.source_job_id == "12345"
        assert job_raw.company == "Test Company"
        assert job_raw.title == "Software Engineer"
        assert job_raw.url == "https://example.com/jobs/12345"
        assert job_raw.fetched_at is not None

    def test_job_raw_string_representation(self):
        """Test string representation of JobRaw."""
        job_raw = JobRaw(
            source="greenhouse",
            source_job_id="12345",
            company="Test Company",
            title="Software Engineer",
            url="https://example.com/jobs/12345",
            fetched_at=datetime.utcnow(),
        )

        str_repr = str(job_raw)
        assert "Test Company" in str_repr
        assert "Software Engineer" in str_repr


class TestJobNormalized:
    """Tests for JobNormalized model."""

    def test_job_normalized_creation(self):
        """Test creating a JobNormalized instance."""
        job = JobNormalized(
            company="Test Company",
            role="Software Engineer",
            priority_score=85.0,
            status=JobStatus.NEW,
        )

        assert job.company == "Test Company"
        assert job.role == "Software Engineer"
        assert job.priority_score == 85.0
        assert job.status == JobStatus.NEW

    def test_job_status_enum(self):
        """Test JobStatus enum values."""
        assert JobStatus.NEW.value == "new"
        assert JobStatus.APPROVED.value == "approved"
        assert JobStatus.REJECTED.value == "rejected"
        assert JobStatus.ARCHIVED.value == "archived"

    def test_job_normalized_string_representation(self):
        """Test string representation of JobNormalized."""
        job = JobNormalized(
            company="Test Company",
            role="Software Engineer",
            priority_score=85.0,
            status=JobStatus.NEW,
        )

        str_repr = str(job)
        assert "Test Company" in str_repr
        assert "Software Engineer" in str_repr


class TestApplication:
    """Tests for Application model."""

    def test_application_creation(self):
        """Test creating an Application instance."""
        application = Application(
            company="Test Company",
            role="Software Engineer",
            stage=ApplicationStage.APPLIED,
            date_applied=datetime.utcnow(),
        )

        assert application.company == "Test Company"
        assert application.role == "Software Engineer"
        assert application.stage == ApplicationStage.APPLIED

    def test_application_stage_enum(self):
        """Test ApplicationStage enum values."""
        assert ApplicationStage.APPLIED.value == "applied"
        assert ApplicationStage.SCREENING.value == "screening"
        assert ApplicationStage.TECHNICAL.value == "technical"
        assert ApplicationStage.ONSITE.value == "onsite"
        assert ApplicationStage.OFFER.value == "offer"
        assert ApplicationStage.REJECTED.value == "rejected"
        assert ApplicationStage.WITHDRAWN.value == "withdrawn"


class TestContact:
    """Tests for Contact model."""

    def test_contact_creation(self):
        """Test creating a Contact instance."""
        contact = Contact(
            company="Test Company",
            name="John Doe",
            role="Hiring Manager",
        )

        assert contact.company == "Test Company"
        assert contact.name == "John Doe"
        assert contact.role == "Hiring Manager"


class TestOutreach:
    """Tests for Outreach model."""

    def test_outreach_creation(self):
        """Test creating an Outreach instance."""
        outreach = Outreach(
            application_id=1,
            contact_id=1,
            outreach_goal="Get referral",
            draft_text="Test message",
        )

        assert outreach.application_id == 1
        assert outreach.contact_id == 1
        assert outreach.outreach_goal == "Get referral"
        assert outreach.draft_text == "Test message"


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_profile_creation(self):
        """Test creating a UserProfile instance."""
        profile = UserProfile(
            full_name="Test User",
            email="test@example.com",
            city="New York",
        )

        assert profile.full_name == "Test User"
        assert profile.email == "test@example.com"
        assert profile.city == "New York"


class TestTrackerEntry:
    """Tests for TrackerEntry model."""

    def test_tracker_entry_creation(self):
        """Test creating a TrackerEntry instance."""
        entry = TrackerEntry(
            application_id=1,
            company="Test Company",
            role="Software Engineer",
            stage="onsite",
        )

        assert entry.application_id == 1
        assert entry.company == "Test Company"
        assert entry.role == "Software Engineer"
        assert entry.stage == "onsite"
