"""
Unit Tests for Job Fetchers

Tests the job fetching functionality.
"""

import pytest
from app.services.fetchers.base import BaseFetcher
from app.services.fetchers.greenhouse import GreenhouseFetcher
from app.services.fetchers.lever import LeverFetcher
from app.services.fetchers.ashby import AshbyFetcher


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


class TestLeverFetcher:
    """Tests for LeverFetcher class."""

    def test_lever_fetcher_initialization(self):
        """Test LeverFetcher initialization."""
        fetcher = LeverFetcher(api_key="test_key")

        assert fetcher.api_key == "test_key"
        assert fetcher.source_name == "lever"

    def test_get_source_name(self):
        """Test getting source name."""
        fetcher = LeverFetcher()

        assert fetcher.get_source_name() == "lever"

    @pytest.mark.asyncio
    async def test_fetch_jobs_requires_company(self):
        """Test that fetch_jobs requires company parameter."""
        fetcher = LeverFetcher()

        with pytest.raises(ValueError, match="Company name is required"):
            await fetcher.fetch_jobs()

    def test_normalize_job(self):
        """Test job normalization."""
        fetcher = LeverFetcher()

        raw_job = {
            "id": "abc123",
            "name": "Example Company",
            "title": "Software Engineer",
            "text": "Job description here",
            "hostedUrl": "https://example.com/jobs/abc123",
            "createdAt": "2024-01-15T00:00:00Z",
            "categories": {
                "location": ["New York, NY", "Remote"],
                "team": "Engineering",
                "commitment": "Full-time"
            }
        }

        normalized = fetcher.normalize_job(raw_job)

        assert normalized["source"] == "lever"
        assert normalized["source_job_id"] == "abc123"
        assert normalized["company"] == "Example Company"
        assert normalized["title"] == "Software Engineer"
        assert normalized["location_raw"] == "New York, NY, Remote"
        assert normalized["ats_type"] == "lever"

    def test_extract_location(self):
        """Test location extraction."""
        fetcher = LeverFetcher()

        raw_job = {
            "categories": {
                "location": ["New York, NY", "Remote"]
            }
        }

        location = fetcher._extract_location(raw_job)
        assert location == "New York, NY, Remote"

    def test_extract_location_empty(self):
        """Test location extraction with empty data."""
        fetcher = LeverFetcher()

        raw_job = {
            "categories": {}
        }

        location = fetcher._extract_location(raw_job)
        assert location == ""


class TestAshbyFetcher:
    """Tests for AshbyFetcher class."""

    def test_ashby_fetcher_initialization(self):
        """Test AshbyFetcher initialization."""
        fetcher = AshbyFetcher(api_key="test_key")

        assert fetcher.api_key == "test_key"
        assert fetcher.source_name == "ashby"

    def test_get_source_name(self):
        """Test getting source name."""
        fetcher = AshbyFetcher()

        assert fetcher.get_source_name() == "ashby"

    @pytest.mark.asyncio
    async def test_fetch_jobs_requires_company(self):
        """Test that fetch_jobs requires company parameter."""
        fetcher = AshbyFetcher()

        with pytest.raises(ValueError, match="Company name is required"):
            await fetcher.fetch_jobs()

    def test_normalize_job(self):
        """Test job normalization."""
        fetcher = AshbyFetcher()

        raw_job = {
            "id": "xyz789",
            "organizationName": "Example Company",
            "title": "Software Engineer",
            "description": "Job description here",
            "jobUrl": "https://example.com/jobs/xyz789",
            "publishedDate": "2024-01-15T00:00:00Z",
            "location": {
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "remote": True
            }
        }

        normalized = fetcher.normalize_job(raw_job)

        assert normalized["source"] == "ashby"
        assert normalized["source_job_id"] == "xyz789"
        assert normalized["company"] == "Example Company"
        assert normalized["title"] == "Software Engineer"
        assert normalized["ats_type"] == "ashby"

    def test_extract_location(self):
        """Test location extraction."""
        fetcher = AshbyFetcher()

        location_data = {
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "remote": True
        }

        location = fetcher._extract_location(location_data)
        assert "New York" in location
        assert "Remote" in location

    def test_extract_location_empty(self):
        """Test location extraction with empty data."""
        fetcher = AshbyFetcher()

        location = fetcher._extract_location({})
        assert location == ""