"""
Simple Integration Tests for API

Tests the API endpoints without database dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """
    Create a test client for FastAPI.

    Yields:
        Test client
    """
    return TestClient(app)


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

    def test_fetch_jobs_invalid_source(self, client: TestClient):
        """Test fetching jobs with invalid source."""
        response = client.post(
            "/api/jobs/fetch",
            json={"sources": ["invalid_source"], "force_refresh": False}
        )

        assert response.status_code == 400

    def test_sync_tracker(self, client: TestClient):
        """Test syncing tracker."""
        response = client.post("/api/tracker/sync")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "status" in data
