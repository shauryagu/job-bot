"""
Integration Tests for Job Fetching API

Tests the job fetching API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from app.models.job import JobRaw, JobStatus
from datetime import datetime


class TestJobFetchingAPI:
    """Tests for job fetching API endpoints."""

    @pytest.fixture
    def client(self, db_session):
        """Create test client."""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        from app.db import session as db_session_module
        app.dependency_overrides[db_session_module.get_db] = override_get_db

        try:
            yield TestClient(app)
        finally:
            app.dependency_overrides.clear()

    def test_fetch_jobs_single_source(self, client):
        """Test fetching jobs from a single source."""
        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [
                {
                    "id": 12345,
                    "title": "Software Engineer",
                    "location": {"name": "New York, NY"},
                    "content": "Job description",
                    "absolute_url": "https://example.com/jobs/12345",
                    "updated_at": "2024-01-15T00:00:00Z",
                    "metadata": [{"company": "Example Company"}]
                }
            ]

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Jobs fetched successfully from 1 sources"
            assert data["total_fetched"] == 1
            assert len(data["sources"]) == 1
            assert data["sources"][0]["source"] == "greenhouse"

    def test_fetch_jobs_multiple_sources(self, client):
        """Test fetching jobs from multiple sources."""
        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_greenhouse, \
             patch('app.services.fetchers.lever.LeverFetcher.fetch_jobs', new_callable=AsyncMock) as mock_lever:

            mock_greenhouse.return_value = [
                {
                    "id": 12345,
                    "title": "Software Engineer",
                    "location": {"name": "New York, NY"},
                    "content": "Job description",
                    "absolute_url": "https://example.com/jobs/12345",
                    "updated_at": "2024-01-15T00:00:00Z",
                    "metadata": [{"company": "Example Company"}]
                }
            ]

            mock_lever.return_value = [
                {
                    "id": "abc123",
                    "name": "Example Company",
                    "title": "Data Scientist",
                    "text": "Job description",
                    "hostedUrl": "https://example.com/jobs/abc123",
                    "createdAt": "2024-01-15T00:00:00Z",
                    "categories": {"location": ["Remote"]}
                }
            ]

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse", "lever"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_fetched"] == 2
            assert len(data["sources"]) == 2

    def test_fetch_jobs_invalid_source(self, client):
        """Test fetching jobs with invalid source."""
        response = client.post(
            "/api/jobs/fetch",
            json={"sources": ["invalid_source"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) == 1
        assert data["sources"][0]["source"] == "invalid_source"
        assert data["sources"][0]["failure_count"] == 1
        assert len(data["sources"][0]["errors"]) > 0

    def test_fetch_jobs_force_refresh(self, client, db_session):
        """Test fetching jobs with force_refresh flag."""
        # Create an existing job
        existing_job = JobRaw(
            source="greenhouse",
            source_job_id="12345",
            company="Example Company",
            title="Software Engineer",
            location_raw="New York, NY",
            description_raw="Old description",
            url="https://example.com/jobs/12345",
            date_posted_raw="2024-01-15T00:00:00Z",
            ats_type="greenhouse",
            metadata_json="{}",
            fetched_at=datetime.utcnow()
        )
        db_session.add(existing_job)
        db_session.commit()

        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [
                {
                    "id": 12345,
                    "title": "Software Engineer",
                    "location": {"name": "New York, NY"},
                    "content": "New description",
                    "absolute_url": "https://example.com/jobs/12345",
                    "updated_at": "2024-01-16T00:00:00Z",
                    "metadata": [{"company": "Example Company"}]
                }
            ]

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse"], "force_refresh": True}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_fetched"] == 1
            assert data["total_skipped"] == 0

    def test_fetch_jobs_deduplication(self, client, db_session):
        """Test that duplicate jobs are skipped."""
        # Create an existing job
        existing_job = JobRaw(
            source="greenhouse",
            source_job_id="12345",
            company="Example Company",
            title="Software Engineer",
            location_raw="New York, NY",
            description_raw="Job description",
            url="https://example.com/jobs/12345",
            date_posted_raw="2024-01-15T00:00:00Z",
            ats_type="greenhouse",
            metadata_json="{}",
            fetched_at=datetime.utcnow()
        )
        db_session.add(existing_job)
        db_session.commit()

        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [
                {
                    "id": 12345,
                    "title": "Software Engineer",
                    "location": {"name": "New York, NY"},
                    "content": "Job description",
                    "absolute_url": "https://example.com/jobs/12345",
                    "updated_at": "2024-01-15T00:00:00Z",
                    "metadata": [{"company": "Example Company"}]
                }
            ]

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse"], "force_refresh": False}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_fetched"] == 0
            assert data["total_skipped"] == 1

    def test_fetch_jobs_response_structure(self, client):
        """Test that response has correct structure."""
        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs') as mock_fetch:
            mock_fetch.return_value = AsyncMock(return_value=[])()

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse"]}
            )

            assert response.status_code == 200
            data = response.json()

            # Check required fields
            assert "message" in data
            assert "total_fetched" in data
            assert "total_skipped" in data
            assert "sources" in data
            assert "force_refresh" in data
            assert "fetch_time_seconds" in data

            # Check source result structure
            if data["sources"]:
                source_result = data["sources"][0]
                assert "source" in source_result
                assert "success_count" in source_result
                assert "failure_count" in source_result
                assert "errors" in source_result

    def test_fetch_jobs_network_error(self, client):
        """Test handling of network errors."""
        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            response = client.post(
                "/api/jobs/fetch",
                json={"sources": ["greenhouse"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_fetched"] == 0
            assert len(data["sources"]) == 1
            assert data["sources"][0]["failure_count"] == 1
            assert len(data["sources"][0]["errors"]) > 0

    def test_fetch_jobs_specific_companies(self, client):
        """Test fetching jobs for specific companies."""
        with patch('app.services.fetchers.greenhouse.GreenhouseFetcher.fetch_jobs', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [
                {
                    "id": 12345,
                    "title": "Software Engineer",
                    "location": {"name": "New York, NY"},
                    "content": "Job description",
                    "absolute_url": "https://example.com/jobs/12345",
                    "updated_at": "2024-01-15T00:00:00Z",
                    "metadata": [{"company": "Example Company A"}]
                }
            ]

            response = client.post(
                "/api/jobs/fetch",
                json={
                    "sources": ["greenhouse"],
                    "companies": ["Example Company A"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_fetched"] == 1
