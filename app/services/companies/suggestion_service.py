"""
Suggestion Service Module

Provides intelligent company suggestions based on fetched jobs.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.company import Company, ATSType, CompanyPriority
from app.core.logging import get_logger


class SuggestionService:
    """Service for intelligent company suggestions."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def suggest_companies_from_jobs(self, fetched_jobs: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Suggest companies based on fetched jobs that aren't in watchlist.

        Args:
            fetched_jobs: List of fetched job dictionaries
            limit: Maximum number of suggestions

        Returns:
            List of company suggestions with metadata
        """
        existing_companies = {c.name for c in self.db.query(Company.name).all()}

        company_stats = {}
        for job in fetched_jobs:
            company_name = job.get("company")
            if not company_name or company_name in existing_companies:
                continue

            if company_name not in company_stats:
                company_stats[company_name] = {
                    "name": company_name,
                    "job_count": 0,
                    "ats_type": self._detect_ats_type(job),
                    "careers_url": job.get("careers_url"),
                    "locations": set(),
                    "avg_priority_score": 0,
                    "total_score": 0,
                }

            stats = company_stats[company_name]
            stats["job_count"] += 1
            stats["total_score"] += job.get("priority_score", 0)

            if job.get("location"):
                stats["locations"].add(job["location"])

        suggestions = []
        for name, stats in company_stats.items():
            stats["avg_priority_score"] = stats["total_score"] / stats["job_count"]
            stats["locations"] = list(stats["locations"])
            stats["suggested_priority"] = self._recommend_priority(stats)
            suggestions.append(stats)

        suggestions.sort(key=lambda x: (x["job_count"], x["avg_priority_score"]), reverse=True)

        return suggestions[:limit]

    def _detect_ats_type(self, job: Dict[str, Any]) -> ATSType:
        """Detect ATS type from job data."""
        url = job.get("url", "")

        if "greenhouse.io" in url:
            return ATSType.GREENHOUSE
        elif "lever.co" in url:
            return ATSType.LEVER
        elif "ashbyhq.com" in url:
            return ATSType.ASHBY
        elif "workday.com" in url:
            return ATSType.WORKDAY
        else:
            return ATSType.OTHER

    def _recommend_priority(self, company_stats: Dict[str, Any]) -> CompanyPriority:
        """Recommend priority level based on job quality."""
        avg_score = company_stats["avg_priority_score"]
        job_count = company_stats["job_count"]

        if avg_score >= 80 and job_count >= 3:
            return CompanyPriority.PRIORITY_5
        elif avg_score >= 70 and job_count >= 2:
            return CompanyPriority.PRIORITY_4
        elif avg_score >= 60:
            return CompanyPriority.PRIORITY_3
        elif avg_score >= 50:
            return CompanyPriority.PRIORITY_2
        else:
            return CompanyPriority.PRIORITY_1
