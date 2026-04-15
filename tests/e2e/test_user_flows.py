"""
End-to-End Tests for User Flows

Tests complete user workflows.
"""

import pytest
from fastapi.testclient import TestClient
from app.models.profile import UserProfile
from app.models.job import JobNormalized, JobStatus, ActionBucket, LocationType
from app.models.application import Application, ApplicationStage


class TestUserProfileFlow:
    """Tests for user profile setup flow."""

    def test_complete_profile_setup_flow(self, client: TestClient, db_session):
        """Test complete user profile setup flow."""
        # Step 1: Check if profile exists (should not exist)
        response = client.get("/api/profile")
        assert response.status_code == 404

        # Step 2: Create profile
        profile_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "linkedin": "https://linkedin.com/in/testuser",
            "github": "https://github.com/testuser",
        }

        response = client.put("/api/profile", json=profile_data)
        assert response.status_code == 200

        data = response.json()
        assert data["full_name"] == "Test User"
        assert data["email"] == "test@example.com"

        # Step 3: Retrieve profile
        response = client.get("/api/profile")
        assert response.status_code == 200

        data = response.json()
        assert data["full_name"] == "Test User"


class TestJobApplicationFlow:
    """Tests for job application flow."""

    def test_job_to_application_flow(self, client: TestClient, db_session):
        """Test complete flow from job to application."""
        # Step 1: Create a test job
        job = JobNormalized(
            company="Test Company",
            role="Software Engineer",
            title_bucket="Backend",
            location_type=LocationType.NYC,
            fit_score=5,
            company_priority=4,
            freshness_score=5,
            location_score=3,
            referral_score=1,
            effort_penalty=0,
            priority_score=18.0,
            action_bucket=ActionBucket.APPLY_NOW,
            status=JobStatus.NEW,
        )

        db_session.add(job)
        db_session.commit()

        # Step 2: Approve the job
        response = client.post(f"/api/jobs/{job.id}/approve")
        assert response.status_code == 200

        # Verify job status changed
        db_session.refresh(job)
        assert job.status == JobStatus.APPROVED

        # Step 3: Create application
        application_data = {
            "job_id": job.id,
            "company": "Test Company",
            "role": "Software Engineer",
            "resume_version": "v1.0",
        }

        response = client.post("/api/applications", json=application_data)
        assert response.status_code == 200

        data = response.json()
        assert data["company"] == "Test Company"
        assert data["role"] == "Software Engineer"
        assert data["stage"] == ApplicationStage.APPLIED

        # Step 4: Update application status
        status_update = {
            "stage": ApplicationStage.SCREENING,
            "next_action": "Prepare for technical interview",
        }

        response = client.put(f"/api/applications/{data['id']}/status", json=status_update)
        assert response.status_code == 200

        # Verify status updated
        response = client.get(f"/api/applications/{data['id']}")
        assert response.status_code == 200

        updated_data = response.json()
        assert updated_data["stage"] == ApplicationStage.SCREENING
        assert updated_data["next_action"] == "Prepare for technical interview"


class TestTrackerSyncFlow:
    """Tests for tracker synchronization flow."""

    def test_tracker_sync_flow(self, client: TestClient):
        """Test tracker synchronization flow."""
        # Step 1: Initiate sync
        response = client.post("/api/tracker/sync")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "status" in data

        # Step 2: Get tracker data
        response = client.get("/api/tracker")
        assert response.status_code == 200

        data = response.json()
        assert "entries" in data
        assert "total" in data