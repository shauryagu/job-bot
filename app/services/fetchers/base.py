"""
Base Fetcher Module

Defines the abstract interface for all job fetchers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models.job import JobRaw


class BaseFetcher(ABC):
    """
    Abstract base class for job fetchers.

    All job fetchers must inherit from this class and implement
    the required methods.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the fetcher.

        Args:
            api_key: Optional API key for authentication
        """
        self.api_key = api_key
        self.source_name = self.__class__.__name__.lower().replace("fetcher", "")

    @abstractmethod
    async def fetch_jobs(self, company: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch jobs from the source.

        Args:
            company: Optional company name to filter by
            limit: Maximum number of jobs to fetch

        Returns:
            List of job dictionaries
        """
        pass

    @abstractmethod
    def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw job data to standard format.

        Args:
            raw_job: Raw job data from source

        Returns:
            Normalized job data
        """
        pass

    def get_source_name(self) -> str:
        """
        Get the source name for this fetcher.

        Returns:
            Source name
        """
        return self.source_name