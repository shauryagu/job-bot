"""
Jobs API Router

Handles job-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.models.job import JobRaw, JobNormalized, JobStatus
from app.schemas.jobs import JobResponse, JobListResponse, JobFetchRequest
from app.services.fetchers.factory import FetcherFactory
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException

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


@router.post("/fetch")
async def fetch_jobs(request: JobFetchRequest, db: Session = Depends(get_db)):
    """
    Fetch jobs from configured sources.

    Args:
        request: Fetch request parameters
        db: Database session

    Returns:
        Fetch results
    """
    try:
        total_fetched = 0
        fetched_jobs = []

        for source in request.sources:
            try:
                fetcher = FetcherFactory.get_fetcher(source)
                logger.info(f"Fetching jobs from {source}")

                # For now, we'll use a default company name
                # In production, this would come from request or config
                raw_jobs = await fetcher.fetch_jobs(company="example", limit=100)

                for raw_job in raw_jobs:
                    # Create JobRaw entry
                    job_raw = JobRaw(
                        source=source,
                        source_job_id=raw_job.get("source_job_id", ""),
                        raw_data=raw_job,
                        fetched_at=datetime.utcnow(),
                    )
                    db.add(job_raw)
                    fetched_jobs.append(raw_job)
                    total_fetched += 1

                logger.info(f"Fetched {len(raw_jobs)} jobs from {source}")

            except ValueError as e:
                logger.error(f"Invalid source {source}: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Failed to fetch jobs from {source}: {e}")
                # Continue with other sources even if one fails
                continue

        db.commit()

        return {
            "message": "Jobs fetched successfully",
            "count": total_fetched,
            "sources": request.sources,
            "force_refresh": request.force_refresh,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch jobs: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")