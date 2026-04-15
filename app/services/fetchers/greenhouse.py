"""
Greenhouse Fetcher Module

Implements job fetching from Greenhouse ATS.
"""

from typing import List, Dict, Any
from app.services.fetchers.base import BaseFetcher
import httpx


class GreenhouseFetcher(BaseFetcher):
    """
    Fetcher for Greenhouse ATS job boards.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Greenhouse fetcher.

        Args:
            api_key: Optional Greenhouse API key
        """
        super().__init__(api_key)
        self.base_url = "https://boards.greenhouse.io"
        self.api_version = "v1"

    async def fetch_jobs(self, company: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Greenhouse.

        Args:
            company: Company name for Greenhouse board
            limit: Maximum number of jobs to fetch

        Returns:
            List of job dictionaries
        """
        if not company:
            raise ValueError("Company name is required for Greenhouse fetcher")

        url = f"{self.base_url}/{company}/jobs/{self.api_version}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()
            jobs = data.get("jobs", [])

            return jobs[:limit]

    def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Greenhouse job data.

        Args:
            raw_job: Raw job data from Greenhouse

        Returns:
            Normalized job data
        """
        return {
            "source": "greenhouse",
            "source_job_id": str(raw_job.get("id")),
            "company": raw_job.get("metadata", []).get("company", ""),
            "title": raw_job.get("title"),
            "location_raw": raw_job.get("location", {}).get("name"),
            "description_raw": raw_job.get("content"),
            "url": raw_job.get("absolute_url"),
            "date_posted_raw": raw_job.get("updated_at"),
            "ats_type": "greenhouse",
            "metadata_json": str(raw_job),
        }