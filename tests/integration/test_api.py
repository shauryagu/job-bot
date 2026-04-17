"""
Integration Tests for API

Tests the API endpoints with database interactions.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
# Import all models to ensure they're registered with SQLAlchemy
from app.models.job import JobRaw, JobNormalized, JobStatus
from app.models.application import Application, ApplicationStage
from app.models.profile import UserProfile
from app.models.tracker import TrackerEntry
from app.models.contact import Contact
from app.models.outreach import Outreach


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"


class TestJobsEndpoints:
    """Tests for jobs endpoints."""

    def test_get_jobs_empty(self, client: TestClient):
        """Test getting jobs when none exist."""
        response = client.get("/api/jobs")

        assert response.status_code == 200
        data = response.json()

        assert "jobs" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["jobs"]) == 0

    def test_get_nonexistent_job(self, client: TestClient):
        """Test getting a job that doesn't exist."""
        response = client.get("/api/jobs/99999")

        assert response.status_code == 404

    def test_approve_nonexistent_job(self, client: TestClient):
        """Test approving a job that doesn't exist."""
        response = client.post("/api/jobs/99999/approve")

        assert response.status_code == 404

    def test_reject_nonexistent_job(self, client: TestClient):
        """Test rejecting a job that doesn't exist."""
        response = client.post("/api/jobs/99999/reject")

        assert response.status_code == 404

    def test_fetch_jobs_invalid_source(self, client: TestClient):
        """Test fetching jobs with invalid source."""
        response = client.post(
            "/api/jobs/fetch",
            json={"sources": ["invalid_source"], "force_refresh": False}
        )

        assert response.status_code == 400


class TestApplicationsEndpoints:
    """Tests for applications endpoints."""

    def test_get_applications_empty(self, client: TestClient):
        """Test getting applications when none exist."""
        response = client.get("/api/applications")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_nonexistent_application(self, client: TestClient):
        """Test getting an application that doesn't exist."""
        response = client.get("/api/applications/99999")

        assert response.status_code == 404

    def test_create_application_invalid_job_id(self, client: TestClient):
        """Test creating application with invalid job ID."""
        response = client.post(
            "/api/applications/",
            json={
                "job_id": 99999,
                "company": "Test Company",
                "role": "Software Engineer",
                "resume_version": "v1.0",
                "notes": "Test notes"
            }
        )

        assert response.status_code == 404

    def test_create_application_missing_fields(self, client: TestClient):
        """Test creating application with missing required fields."""
        response = client.post(
            "/api/applications/",
            json={
                "company": "Test Company",
                # Missing role
            }
        )

        assert response.status_code == 422  # Validation error


class TestProfileEndpoints:
    """Tests for profile endpoints."""

    def test_get_profile_not_found(self, client: TestClient):
        """Test getting profile when none exists."""
        response = client.get("/api/profile")

        # Should return 404 when no profile exists
        assert response.status_code == 404

    def test_update_profile(self, client: TestClient):
        """Test updating profile."""
        response = client.put(
            "/api/profile",
            json={
                "full_name": "Test User",
                "email": "test@example.com",
                "phone": "555-1234",
                "linkedin": "https://linkedin.com/in/test",
                "github": "https://github.com/test"
            }
        )

        # Should create profile if none exists
        assert response.status_code == 200
        data = response.json()

        assert data["full_name"] == "Test User"
        assert data["email"] == "test@example.com"


class TestOutreachEndpoints:
    """Tests for outreach endpoints."""

    def test_get_contacts_for_company(self, client: TestClient):
        """Test getting contacts for a company."""
        response = client.get("/api/outreach/contacts/Test Company")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_mark_outreach_sent_nonexistent(self, client: TestClient):
        """Test marking outreach as sent for non-existent outreach."""
        response = client.post("/api/outreach/99999/send")

        assert response.status_code == 404


class TestTrackerEndpoints:
    """Tests for tracker endpoints."""

    def test_get_tracker_data(self, client: TestClient):
        """Test getting tracker data."""
        response = client.get("/api/tracker/")

        assert response.status_code == 200
        data = response.json()

        assert "entries" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    def test_sync_tracker(self, client: TestClient):
        """Test syncing tracker."""
        response = client.post("/api/tracker/sync")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "status" in data


class TestErrorHandling:
    """Tests for error handling across endpoints."""

    def test_invalid_json_format(self, client: TestClient):
        """Test sending invalid JSON format."""
        response = client.post(
            "/api/applications/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_missing_content_type(self, client: TestClient):
        """Test request without proper content type."""
        response = client.post(
            "/api/applications/",
            json={"company": "Test"},
            headers={"Content-Type": "text/plain"}
        )

        # Should still work as FastAPI handles this
        assert response.status_code in [200, 422]