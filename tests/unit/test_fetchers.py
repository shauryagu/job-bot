"""
Unit Tests for Job Fetchers

Tests the job fetching functionality.
"""

import pytest
from app.services.fetchers.base import BaseFetcher
from app.services.fetchers.greenhouse import GreenhouseFetcher


class TestBaseFetcher:
    """Tests for BaseFetcher class."""

    def test_base_fetcher_is_abstract(self):
        """Test that BaseFetcher cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFetcher()


class TestGreenhouseFetcher:
    """Tests for GreenhouseFetcher class."""

    def test_greenhouse_fetcher_initialization(self):
        """Test GreenhouseFetcher initialization."""
        fetcher = GreenhouseFetcher(api_key="test_key")

        assert fetcher.api_key == "test_key"
        assert fetcher.source_name == "greenhouse"

    def test_get_source_name(self):
        """Test getting source name."""
        fetcher = GreenhouseFetcher()

        assert fetcher.get_source_name() == "greenhouse"

    @pytest.mark.asyncio
    async def test_fetch_jobs_requires_company(self):
        """Test that fetch_jobs requires company parameter."""
        fetcher = GreenhouseFetcher()

        with pytest.raises(ValueError, match="Company name is required"):
            await fetcher.fetch_jobs()

    def test_normalize_job(self):
        """Test job normalization."""
        fetcher = GreenhouseFetcher()

        raw_job = {
            "id": 12345,
            "title": "Software Engineer",
            "location": {"name": "New York, NY"},
            "content": "Job description here",
            "absolute_url": "https://example.com/jobs/12345",
            "updated_at": "2024-01-15T00:00:00Z",
            "metadata": [{"company": "Example Company"}],
        }

        normalized = fetcher.normalize_job(raw_job)

        assert normalized["source"] == "greenhouse"
        assert normalized["source_job_id"] == "12345"
        assert normalized["title"] == "Software Engineer"
        assert normalized["location_raw"] == "New York, NY"
        assert normalized["ats_type"] == "greenhouse"