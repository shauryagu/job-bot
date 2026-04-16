"""
Fetcher Factory Module

Creates fetcher instances based on source type.
"""

from typing import Dict, Type
from app.services.fetchers.base import BaseFetcher
from app.services.fetchers.greenhouse import GreenhouseFetcher


class FetcherFactory:
    """
    Factory for creating job fetcher instances.
    """

    _fetchers: Dict[str, Type[BaseFetcher]] = {
        "greenhouse": GreenhouseFetcher,
        # Add more fetchers as they are implemented
        # "lever": LeverFetcher,
        # "ashby": AshbyFetcher,
        # "manual": ManualFetcher,
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
        fetcher_class = cls._fetchers.get(source.lower())
        if not fetcher_class:
            raise ValueError(
                f"Unknown fetcher: {source}. "
                f"Supported sources: {', '.join(cls._fetchers.keys())}"
            )
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
