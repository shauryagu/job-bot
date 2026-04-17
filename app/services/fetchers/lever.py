"""
Lever Fetcher Module

Implements job fetching from Lever ATS.
"""

from typing import List, Dict, Any
from app.services.fetchers.base import BaseFetcher
from app.core.logging import get_logger
import httpx

logger = get_logger(__name__)


class LeverFetcher(BaseFetcher):
    """
    Fetcher for Lever ATS job boards.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Lever fetcher.

        Args:
            api_key: Optional Lever API key
        """
        super().__init__(api_key)
        self.base_url = "https://jobs.lever.co"
        self.api_version = "v0"

    async def fetch_jobs(self, company: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Lever.

        Args:
            company: Company name for Lever board
            limit: Maximum number of jobs to fetch

        Returns:
            List of job dictionaries
        """
        if not company:
            raise ValueError("Company name is required for Lever fetcher")

        url = f"{self.base_url}/{self.api_version}/postings/{company}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                data = response.json()
                jobs = data if isinstance(data, list) else data.get("data", [])

                return jobs[:limit]

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching jobs from Lever for {company}: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching jobs from Lever for {company}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching jobs from Lever for {company}: {e}")
            raise

    def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Lever job data.

        Args:
            raw_job: Raw job data from Lever

        Returns:
            Normalized job data
        """
        categories = raw_job.get("categories", {})
        text = raw_job.get("text", "")

        return {
            "source": "lever",
            "source_job_id": str(raw_job.get("id", "")),
            "company": raw_job.get("name", ""),
            "title": raw_job.get("title", ""),
            "location_raw": self._extract_location(raw_job),
            "description_raw": text,
            "url": raw_job.get("hostedUrl", ""),
            "date_posted_raw": raw_job.get("createdAt", ""),
            "ats_type": "lever",
            "metadata_json": str(raw_job),
        }

    def _extract_location(self, raw_job: Dict[str, Any]) -> str:
        """
        Extract location from Lever job data.

        Args:
            raw_job: Raw job data from Lever

        Returns:
            Location string
        """
        locations = raw_job.get("categories", {}).get("location", [])
        if locations and isinstance(locations, list):
            return ", ".join(locations)
        return ""
