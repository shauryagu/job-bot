"""
Fetcher Factory Module

Creates fetcher instances based on source type.
"""

from typing import Dict, Type, Optional
from app.services.fetchers.base import BaseFetcher
from app.services.fetchers.greenhouse import GreenhouseFetcher
from app.services.fetchers.lever import LeverFetcher
from app.services.fetchers.ashby import AshbyFetcher
from app.core.logging import get_logger

logger = get_logger(__name__)


class FetcherFactory:
    """
    Factory for creating job fetcher instances.
    """

    _fetchers: Dict[str, Type[BaseFetcher]] = {
        "greenhouse": GreenhouseFetcher,
        "lever": LeverFetcher,
        "ashby": AshbyFetcher,
    }

    _fetcher_info: Dict[str, Dict[str, any]] = {
        "greenhouse": {
            "requires_api_key": False,
            "supported_params": ["company", "limit"],
            "description": "Greenhouse ATS job boards",
        },
        "lever": {
            "requires_api_key": False,
            "supported_params": ["company", "limit"],
            "description": "Lever ATS job boards",
        },
        "ashby": {
            "requires_api_key": True,
            "supported_params": ["company", "limit"],
            "description": "Ashby ATS job boards",
        },
    }

    @classmethod
    def get_fetcher(cls, source: str, api_key: str = None) -> BaseFetcher:
        """
        Get a fetcher instance for the specified source.

        Args:
            source: Source name (e.g., "greenhouse", "lever")
            api_key: Optional API key for authentication

        Returns:
            Fetcher instance

        Raises:
            ValueError: If source is not supported
        """
        source_lower = source.lower()
        fetcher_class = cls._fetchers.get(source_lower)

        if not fetcher_class:
            raise ValueError(
                f"Unknown fetcher: {source}. "
                f"Supported sources: {', '.join(cls._fetchers.keys())}"
            )

        fetcher_info = cls._fetcher_info.get(source_lower, {})
        requires_api_key = fetcher_info.get("requires_api_key", False)

        if requires_api_key and not api_key:
            logger.warning(f"API key required for {source} but not provided")

        return fetcher_class(api_key=api_key)

    @classmethod
    def register_fetcher(cls, source: str, fetcher_class: Type[BaseFetcher]) -> None:
        """
        Register a new fetcher type.

        Args:
            source: Source name
            fetcher_class: Fetcher class to register
        """
        cls._fetchers[source.lower()] = fetcher_class

    @classmethod
    def get_supported_sources(cls) -> list[str]:
        """
        Get list of supported sources.

        Returns:
            List of source names
        """
        return list(cls._fetchers.keys())

    @classmethod
    def get_fetcher_info(cls, source: str) -> Optional[Dict[str, any]]:
        """
        Get metadata about a fetcher.

        Args:
            source: Source name

        Returns:
            Fetcher metadata dictionary or None if not found
        """
        return cls._fetcher_info.get(source.lower())

    @classmethod
    def get_all_fetcher_info(cls) -> Dict[str, Dict[str, any]]:
        """
        Get metadata for all registered fetchers.

        Returns:
            Dictionary mapping source names to their metadata
        """
        return cls._fetcher_info.copy()
