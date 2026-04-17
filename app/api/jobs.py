"""
Jobs API Router

Handles job-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.job import JobRaw, JobNormalized, JobStatus
from app.schemas.jobs import JobResponse, JobListResponse, JobFetchRequest, JobFetchResponse, JobFetchSourceResult
from app.services.fetchers.factory import FetcherFactory
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException, ExternalAPIException, RateLimitException
from app.core.config import settings, get_companies_by_ats_type, get_company_config
import time

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    status: Optional[JobStatus] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get all jobs with optional filtering.

    Args:
        status: Filter by job status
        source: Filter by job source
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        List of jobs
    """
    try:
        query = db.query(JobNormalized)

        if status:
            query = query.filter(JobNormalized.status == status)

        if source:
            query = query.join(JobNormalized.raw_job).filter(JobRaw.source == source)

        jobs = query.order_by(JobNormalized.priority_score.desc()).offset(offset).limit(limit).all()

        total = query.count()

        return JobListResponse(
            jobs=jobs,
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Get a specific job by ID.

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        Job details
    """
    try:
        job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/{job_id}/approve")
async def approve_job(job_id: int, db: Session = Depends(get_db)):
    """
    Approve a job for application.

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        Updated job
    """
    try:
        job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.status = JobStatus.APPROVED
        db.commit()

        logger.info(f"Approved job {job_id}")
        return {"message": "Job approved successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve job {job_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/{job_id}/reject")
async def reject_job(job_id: int, db: Session = Depends(get_db)):
    """
    Reject a job.

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        Updated job
    """
    try:
        job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.status = JobStatus.REJECTED
        db.commit()

        logger.info(f"Rejected job {job_id}")
        return {"message": "Job rejected successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject job {job_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/fetch", response_model=JobFetchResponse)
async def fetch_jobs(request: JobFetchRequest, db: Session = Depends(get_db)):
    """
    Fetch jobs from configured sources.

    Args:
        request: Fetch request parameters
        db: Database session

    Returns:
        Fetch results with per-source statistics
    """
    start_time = time.time()
    total_fetched = 0
    total_skipped = 0
    source_results = []

    try:
        for source in request.sources:
            source_result = JobFetchSourceResult(source=source)

            try:
                fetcher = FetcherFactory.get_fetcher(source)
                logger.info(f"Fetching jobs from {source}")

                # Get companies for this ATS type
                companies = get_companies_by_ats_type(source)

                if not companies:
                    logger.warning(f"No companies configured for {source}")
                    source_result.errors.append(f"No companies configured for {source}")
                    source_results.append(source_result)
                    continue

                # If specific companies requested, filter
                if request.companies:
                    companies = [c for c in companies if c["name"] in request.companies]

                if not companies:
                    logger.warning(f"No matching companies for {source} with specified companies")
                    source_result.errors.append(f"No matching companies for {source}")
                    source_results.append(source_result)
                    continue

                # Fetch jobs for each company
                for company_config in companies:
                    company_name = company_config.get("name")
                    company_slug = company_name.lower().replace(" ", "-")

                    try:
                        raw_jobs = await fetcher.fetch_jobs(
                            company=company_slug,
                            limit=settings.max_jobs_per_source
                        )

                        for raw_job in raw_jobs:
                            # Normalize job data
                            normalized_job = fetcher.normalize_job(raw_job)

                            # Check for duplicates
                            source_job_id = normalized_job.get("source_job_id", "")
                            existing_job = db.query(JobRaw).filter(
                                JobRaw.source == source,
                                JobRaw.source_job_id == source_job_id
                            ).first()

                            if existing_job:
                                if request.force_refresh:
                                    # Update existing job
                                    existing_job.raw_data = raw_job
                                    existing_job.fetched_at = datetime.utcnow()
                                    logger.debug(f"Updated existing job {source_job_id}")
                                else:
                                    total_skipped += 1
                                    logger.debug(f"Skipped duplicate job {source_job_id}")
                                    continue

                            # Create JobRaw entry
                            job_raw = JobRaw(
                                source=source,
                                source_job_id=source_job_id,
                                company=normalized_job.get("company", company_name),
                                title=normalized_job.get("title", ""),
                                location_raw=normalized_job.get("location_raw", ""),
                                description_raw=normalized_job.get("description_raw", ""),
                                url=normalized_job.get("url", ""),
                                date_posted_raw=normalized_job.get("date_posted_raw", ""),
                                ats_type=normalized_job.get("ats_type", source),
                                metadata_json=normalized_job.get("metadata_json", ""),
                                fetched_at=datetime.utcnow(),
                            )
                            db.add(job_raw)
                            total_fetched += 1

                        source_result.success_count += len(raw_jobs)
                        logger.info(f"Fetched {len(raw_jobs)} jobs from {source} for {company_name}")

                    except RateLimitException as e:
                        logger.warning(f"Rate limit exceeded for {source} - {company_name}: {e}")
                        source_result.failure_count += 1
                        source_result.errors.append(f"Rate limit exceeded for {company_name}")
                        continue

                    except ExternalAPIException as e:
                        logger.error(f"External API error for {source} - {company_name}: {e}")
                        source_result.failure_count += 1
                        source_result.errors.append(f"API error for {company_name}: {str(e)}")
                        continue

                    except Exception as e:
                        logger.error(f"Failed to fetch jobs from {source} for {company_name}: {e}")
                        source_result.failure_count += 1
                        source_result.errors.append(f"Error for {company_name}: {str(e)}")
                        continue

                source_results.append(source_result)

            except ValueError as e:
                logger.error(f"Invalid source {source}: {e}")
                source_result.failure_count += 1
                source_result.errors.append(str(e))
                source_results.append(source_result)
                continue

            except Exception as e:
                logger.error(f"Failed to initialize fetcher for {source}: {e}")
                source_result.failure_count += 1
                source_result.errors.append(f"Failed to initialize fetcher: {str(e)}")
                source_results.append(source_result)
                continue

        db.commit()

        fetch_time = time.time() - start_time

        return JobFetchResponse(
            message=f"Jobs fetched successfully from {len(source_results)} sources",
            total_fetched=total_fetched,
            total_skipped=total_skipped,
            sources=source_results,
            force_refresh=request.force_refresh,
            fetch_time_seconds=round(fetch_time, 2),
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Failed to fetch jobs: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")