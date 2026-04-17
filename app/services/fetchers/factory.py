"""
Fetcher Factory Module

Creates fetcher instances based on source type.
"""

from typing import Dict, Type, List, Optional
from sqlalchemy.orm import Session
import json
from app.services.fetchers.base import BaseFetcher
from app.services.fetchers.greenhouse import GreenhouseFetcher
from app.models.company import Company, CompanyStatus, ATSType
from app.models.job import JobRaw
from app.core.logging import get_logger


logger = get_logger(__name__)


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
                f"Unknown fetcher: {source}. " f"Supported sources: {', '.join(cls._fetchers.keys())}"
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

    @classmethod
    async def fetch_for_companies(
        cls,
        db: Session,
        company_ids: Optional[List[int]] = None,
        ats_types: Optional[List[ATSType]] = None,
        force_refresh: bool = False,
    ) -> Dict[str, any]:
        """
        Fetch jobs for specific companies.

        Args:
            db: Database session
            company_ids: Optional list of company IDs to fetch for
            ats_types: Optional list of ATS types to fetch for
            force_refresh: Whether to force refresh

        Returns:
            Fetch results
        """
        from app.services.companies import CompanyService

        service = CompanyService(db)
        results = {"total_fetched": 0, "companies_processed": [], "errors": []}

        # Get companies to fetch for
        if company_ids:
            companies = [service.get_company(cid) for cid in company_ids]
        elif ats_types:
            companies = []
            for ats_type in ats_types:
                companies.extend(service.get_companies_by_ats_type(ats_type))
        else:
            companies, _ = service.list_companies(status=CompanyStatus.ACTIVE)

        # Fetch jobs for each company
        for company in companies:
            if company.status != CompanyStatus.ACTIVE:
                continue

            try:
                fetcher = cls.get_fetcher(company.ats_type.value)
                logger.info(f"Fetching jobs for {company.name} from {company.ats_type.value}")

                raw_jobs = await fetcher.fetch_jobs(company=company.name, limit=100)

                for raw_job in raw_jobs:
                    job_raw = JobRaw(
                        source=company.ats_type.value,
                        source_job_id=raw_job.get("source_job_id", ""),
                        company=company.name,
                        title=raw_job.get("title", ""),
                        location_raw=raw_job.get("location", ""),
                        description_raw=raw_job.get("description", ""),
                        url=raw_job.get("url", ""),
                        date_posted_raw=raw_job.get("date_posted", ""),
                        ats_type=company.ats_type.value,
                        metadata_json=json.dumps(raw_job.get("metadata", {})),
                    )
                    db.add(job_raw)

                db.commit()
                results["total_fetched"] += len(raw_jobs)
                results["companies_processed"].append(
                    {"company_id": company.id, "company_name": company.name, "jobs_fetched": len(raw_jobs)}
                )

                logger.info(f"Fetched {len(raw_jobs)} jobs for {company.name}")

            except Exception as e:
                logger.error(f"Failed to fetch jobs for {company.name}: {e}")
                results["errors"].append(
                    {"company_id": company.id, "company_name": company.name, "error": str(e)}
                )

        return results
