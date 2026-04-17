"""
Ashby Fetcher Module

Implements job fetching from Ashby ATS.
"""

from typing import List, Dict, Any
from app.services.fetchers.base import BaseFetcher
from app.core.logging import get_logger
from app.core.exceptions import ExternalAPIException
import httpx

logger = get_logger(__name__)


class AshbyFetcher(BaseFetcher):
    """
    Fetcher for Ashby ATS job boards.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Ashby fetcher.

        Args:
            api_key: Ashby API key (required for production use)
        """
        super().__init__(api_key)
        self.base_url = "https://api.ashbyhq.com"

    async def fetch_jobs(self, company: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Ashby.

        Args:
            company: Organization name for Ashby
            limit: Maximum number of jobs to fetch

        Returns:
            List of job dictionaries
        """
        if not company:
            raise ValueError("Company name is required for Ashby fetcher")

        url = f"{self.base_url}/posting.get_job_postings_for_organization"

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "includeNonPublishedJobs": False,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()

                if data.get("success"):
                    jobs = data.get("results", {}).get("jobPostings", [])
                    return jobs[:limit]
                else:
                    error_msg = data.get("errors", [{"message": "Unknown error"}])[0].get("message", "Unknown error")
                    raise ExternalAPIException(
                        f"Ashby API error: {error_msg}",
                        service="ashby",
                        status_code=response.status_code
                    )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching jobs from Ashby for {company}: {e}")
            raise ExternalAPIException(
                f"HTTP error fetching jobs from Ashby: {str(e)}",
                service="ashby",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Request error fetching jobs from Ashby for {company}: {e}")
            raise ExternalAPIException(
                f"Request error fetching jobs from Ashby: {str(e)}",
                service="ashby"
            )
        except ExternalAPIException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching jobs from Ashby for {company}: {e}")
            raise ExternalAPIException(
                f"Unexpected error fetching jobs from Ashby: {str(e)}",
                service="ashby"
            )

    def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Ashby job data.

        Args:
            raw_job: Raw job data from Ashby

        Returns:
            Normalized job data
        """
        location_data = raw_job.get("location", {})
        employment_type = raw_job.get("employmentType", "")

        return {
            "source": "ashby",
            "source_job_id": str(raw_job.get("id", "")),
            "company": raw_job.get("organizationName", ""),
            "title": raw_job.get("title", ""),
            "location_raw": self._extract_location(location_data),
            "description_raw": raw_job.get("description", ""),
            "url": raw_job.get("jobUrl", ""),
            "date_posted_raw": raw_job.get("publishedDate", ""),
            "ats_type": "ashby",
            "metadata_json": str(raw_job),
        }

    def _extract_location(self, location_data: Dict[str, Any]) -> str:
        """
        Extract location from Ashby job data.

        Args:
            location_data: Location data from Ashby

        Returns:
            Location string
        """
        if not location_data:
            return ""

        parts = []
        if location_data.get("city"):
            parts.append(location_data["city"])
        if location_data.get("state"):
            parts.append(location_data["state"])
        if location_data.get("country"):
            parts.append(location_data["country"])

        location = ", ".join(parts)

        if location_data.get("remote"):
            if location:
                location = f"{location} (Remote)"
            else:
                location = "Remote"

        return location
