"""
Integration Tests for API

Tests the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


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


class TestProfileEndpoints:
    """Tests for profile endpoints."""

    def test_get_profile_not_found(self, client: TestClient):
        """Test getting profile when none exists."""
        response = client.get("/api/profile")

        # Should return 404 when no profile exists
        assert response.status_code == 404