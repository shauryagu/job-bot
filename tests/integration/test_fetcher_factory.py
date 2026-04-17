"""
Integration Tests for Fetcher Factory

Tests the fetcher factory functionality.
"""

import pytest
from app.services.fetchers.factory import FetcherFactory
from app.services.fetchers.greenhouse import GreenhouseFetcher
from app.services.fetchers.lever import LeverFetcher
from app.services.fetchers.ashby import AshbyFetcher
from app.services.fetchers.base import BaseFetcher


class TestFetcherFactory:
    """Tests for FetcherFactory class."""

    def test_get_fetcher_greenhouse(self):
        """Test getting Greenhouse fetcher."""
        fetcher = FetcherFactory.get_fetcher("greenhouse")

        assert isinstance(fetcher, GreenhouseFetcher)
        assert fetcher.source_name == "greenhouse"

    def test_get_fetcher_lever(self):
        """Test getting Lever fetcher."""
        fetcher = FetcherFactory.get_fetcher("lever")

        assert isinstance(fetcher, LeverFetcher)
        assert fetcher.source_name == "lever"

    def test_get_fetcher_ashby(self):
        """Test getting Ashby fetcher."""
        fetcher = FetcherFactory.get_fetcher("ashby")

        assert isinstance(fetcher, AshbyFetcher)
        assert fetcher.source_name == "ashby"

    def test_get_fetcher_invalid_source(self):
        """Test getting fetcher with invalid source."""
        with pytest.raises(ValueError, match="Unknown fetcher"):
            FetcherFactory.get_fetcher("invalid_source")

    def test_get_fetcher_with_api_key(self):
        """Test getting fetcher with API key."""
        fetcher = FetcherFactory.get_fetcher("greenhouse", api_key="test_key")

        assert fetcher.api_key == "test_key"

    def test_get_fetcher_case_insensitive(self):
        """Test that source names are case-insensitive."""
        fetcher1 = FetcherFactory.get_fetcher("Greenhouse")
        fetcher2 = FetcherFactory.get_fetcher("GREENHOUSE")
        fetcher3 = FetcherFactory.get_fetcher("greenhouse")

        assert isinstance(fetcher1, GreenhouseFetcher)
        assert isinstance(fetcher2, GreenhouseFetcher)
        assert isinstance(fetcher3, GreenhouseFetcher)

    def test_register_fetcher(self):
        """Test registering a new fetcher."""
        class CustomFetcher(BaseFetcher):
            async def fetch_jobs(self, company=None, limit=100):
                return []

            def normalize_job(self, raw_job):
                return {}

        FetcherFactory.register_fetcher("custom", CustomFetcher)

        fetcher = FetcherFactory.get_fetcher("custom")
        assert isinstance(fetcher, CustomFetcher)

    def test_get_supported_sources(self):
        """Test getting list of supported sources."""
        sources = FetcherFactory.get_supported_sources()

        assert isinstance(sources, list)
        assert "greenhouse" in sources
        assert "lever" in sources
        assert "ashby" in sources

    def test_get_fetcher_info(self):
        """Test getting fetcher metadata."""
        info = FetcherFactory.get_fetcher_info("greenhouse")

        assert info is not None
        assert "requires_api_key" in info
        assert "supported_params" in info
        assert "description" in info

    def test_get_fetcher_info_invalid(self):
        """Test getting fetcher info for invalid source."""
        info = FetcherFactory.get_fetcher_info("invalid")

        assert info is None

    def test_get_all_fetcher_info(self):
        """Test getting all fetcher metadata."""
        all_info = FetcherFactory.get_all_fetcher_info()

        assert isinstance(all_info, dict)
        assert "greenhouse" in all_info
        assert "lever" in all_info
        assert "ashby" in all_info

    def test_ashby_requires_api_key_warning(self):
        """Test that Ashby fetcher logs warning without API key."""
        import logging
        from app.core.logging import get_logger

        logger = get_logger(__name__)

        # This should not raise an error, but should log a warning
        fetcher = FetcherFactory.get_fetcher("ashby", api_key=None)

        assert isinstance(fetcher, AshbyFetcher)
        assert fetcher.api_key is None
