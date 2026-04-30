"""
Integration Tests for Company API

Tests the company API endpoints with database interactions.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.company import CompanyPriority, CompanyStatus, ATSType


class TestCompanyEndpoints:
    """Tests for company API endpoints."""

    def test_get_companies_empty(self, client: TestClient):
        """Test getting companies when none exist."""
        response = client.get("/api/companies/")

        assert response.status_code == 200
        data = response.json()

        assert "companies" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["companies"]) == 0

    def test_create_company(self, client: TestClient):
        """Test creating a company."""
        response = client.post(
            "/api/companies/",
            json={
                "name": "Test Company",
                "priority": 5,
                "ats_type": "greenhouse",
                "careers_url": "https://test.com/careers",
                "locations": ["New York", "Remote"],
                "notes": "Test notes",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Test Company"
        assert data["priority"] == 5
        assert data["ats_type"] == "greenhouse"
        assert data["careers_url"] == "https://test.com/careers"
        assert data["locations"] == ["New York", "Remote"]
        assert data["notes"] == "Test notes"
        assert data["status"] == "active"

    def test_create_company_minimal(self, client: TestClient):
        """Test creating a company with minimal data."""
        response = client.post("/api/companies/", json={"name": "Minimal Company"})

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Minimal Company"
        assert data["priority"] == 3  # Default
        assert data["ats_type"] == "other"  # Default
        assert data["status"] == "active"  # Default

    def test_create_duplicate_company(self, client: TestClient):
        """Test creating duplicate company."""
        client.post("/api/companies/", json={"name": "Duplicate Company"})

        response = client.post("/api/companies/", json={"name": "Duplicate Company"})

        assert response.status_code == 400

    def test_create_company_invalid_name(self, client: TestClient):
        """Test creating company with invalid name."""
        response = client.post("/api/companies/", json={"name": ""})

        assert response.status_code == 422  # Validation error

    def test_get_company(self, client: TestClient):
        """Test getting a specific company."""
        create_response = client.post("/api/companies/", json={"name": "Test Company"})
        company_id = create_response.json()["id"]

        response = client.get(f"/api/companies/{company_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == company_id
        assert data["name"] == "Test Company"

    def test_get_nonexistent_company(self, client: TestClient):
        """Test getting non-existent company."""
        response = client.get("/api/companies/99999")

        assert response.status_code == 404

    def test_update_company(self, client: TestClient):
        """Test updating a company."""
        create_response = client.post("/api/companies/", json={"name": "Original Name", "priority": 3})
        company_id = create_response.json()["id"]

        response = client.put(f"/api/companies/{company_id}", json={"name": "Updated Name", "priority": 5})

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Name"
        assert data["priority"] == 5

    def test_update_company_partial(self, client: TestClient):
        """Test partial update of company."""
        create_response = client.post(
            "/api/companies/", json={"name": "Test Company", "priority": 3, "ats_type": "greenhouse"}
        )
        company_id = create_response.json()["id"]

        response = client.put(f"/api/companies/{company_id}", json={"priority": 5})

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Test Company"  # Unchanged
        assert data["priority"] == 5  # Updated
        assert data["ats_type"] == "greenhouse"  # Unchanged

    def test_update_nonexistent_company(self, client: TestClient):
        """Test updating non-existent company."""
        response = client.put("/api/companies/99999", json={"name": "Test"})

        assert response.status_code == 404

    def test_delete_company(self, client: TestClient):
        """Test deleting a company."""
        create_response = client.post("/api/companies/", json={"name": "Test Company"})
        company_id = create_response.json()["id"]

        response = client.delete(f"/api/companies/{company_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Company deleted successfully"
        assert data["company_id"] == company_id

        get_response = client.get(f"/api/companies/{company_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_company(self, client: TestClient):
        """Test deleting non-existent company."""
        response = client.delete("/api/companies/99999")

        assert response.status_code == 404

    def test_pause_company(self, client: TestClient):
        """Test pausing a company."""
        create_response = client.post("/api/companies/", json={"name": "Test Company", "status": "active"})
        company_id = create_response.json()["id"]

        response = client.post(f"/api/companies/{company_id}/pause")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "paused"

    def test_activate_company(self, client: TestClient):
        """Test activating a company."""
        create_response = client.post("/api/companies/", json={"name": "Test Company", "status": "paused"})
        company_id = create_response.json()["id"]

        response = client.post(f"/api/companies/{company_id}/activate")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "active"

    def test_get_companies_by_ats_type(self, client: TestClient):
        """Test getting companies by ATS type."""
        client.post("/api/companies/", json={"name": "Company A", "ats_type": "greenhouse"})
        client.post("/api/companies/", json={"name": "Company B", "ats_type": "lever"})
        client.post("/api/companies/", json={"name": "Company C", "ats_type": "greenhouse"})

        response = client.get("/api/companies/by-ats/greenhouse")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert all(c["ats_type"] == "greenhouse" for c in data)

    def test_search_companies(self, client: TestClient):
        """Test searching companies."""
        client.post("/api/companies/", json={"name": "Tech Company"})
        client.post("/api/companies/", json={"name": "Finance Company"})
        client.post("/api/companies/", json={"name": "Tech Startup"})

        response = client.get("/api/companies/search/Tech")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert all("Tech" in c["name"] for c in data)

    def test_filter_companies_by_status(self, client: TestClient):
        """Test filtering companies by status."""
        client.post("/api/companies/", json={"name": "Active Company", "status": "active"})
        client.post("/api/companies/", json={"name": "Paused Company", "status": "paused"})

        response = client.get("/api/companies/?status=active")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["companies"][0]["name"] == "Active Company"

    def test_filter_companies_by_priority(self, client: TestClient):
        """Test filtering companies by priority."""
        client.post("/api/companies/", json={"name": "Priority 5 Company", "priority": 5})
        client.post("/api/companies/", json={"name": "Priority 3 Company", "priority": 3})

        response = client.get("/api/companies/?priority=5")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["companies"][0]["priority"] == 5

    def test_filter_companies_by_ats_type(self, client: TestClient):
        """Test filtering companies by ATS type."""
        client.post("/api/companies/", json={"name": "Greenhouse Company", "ats_type": "greenhouse"})
        client.post("/api/companies/", json={"name": "Lever Company", "ats_type": "lever"})

        response = client.get("/api/companies/?ats_type=greenhouse")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["companies"][0]["ats_type"] == "greenhouse"

    def test_list_companies_pagination(self, client: TestClient):
        """Test listing companies with pagination."""
        for i in range(5):
            client.post("/api/companies/", json={"name": f"Company {i}"})

        response = client.get("/api/companies/?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert len(data["companies"]) == 2

    def test_list_companies_multiple_filters(self, client: TestClient):
        """Test listing companies with multiple filters."""
        client.post("/api/companies/", json={"name": "Active Greenhouse 5", "status": "active", "ats_type": "greenhouse", "priority": 5})
        client.post("/api/companies/", json={"name": "Active Greenhouse 3", "status": "active", "ats_type": "greenhouse", "priority": 3})
        client.post("/api/companies/", json={"name": "Paused Greenhouse 5", "status": "paused", "ats_type": "greenhouse", "priority": 5})

        response = client.get("/api/companies/?status=active&ats_type=greenhouse&priority=5")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["companies"][0]["name"] == "Active Greenhouse 5"

    def test_company_response_structure(self, client: TestClient):
        """Test company response has correct structure."""
        response = client.post(
            "/api/companies/",
            json={
                "name": "Test Company",
                "priority": 5,
                "ats_type": "greenhouse",
                "careers_url": "https://test.com/careers",
                "locations": ["New York"],
                "notes": "Test",
            },
        )

        assert response.status_code == 200
        data = response.json()

        required_fields = ["id", "name", "priority", "ats_type", "careers_url", "locations", "notes", "status", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data
