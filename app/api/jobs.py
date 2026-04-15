"""
Jobs API Router

Handles job-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.job import JobNormalized, JobStatus
from app.schemas.jobs import JobResponse, JobListResponse, JobFetchRequest

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
    job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


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
    job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = JobStatus.APPROVED
    db.commit()

    return {"message": "Job approved successfully", "job_id": job_id}


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
    job = db.query(JobNormalized).filter(JobNormalized.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = JobStatus.REJECTED
    db.commit()

    return {"message": "Job rejected successfully", "job_id": job_id}


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
    # TODO: Implement job fetching logic
    return {
        "message": "Job fetch initiated",
        "sources": request.sources,
        "force_refresh": request.force_refresh,
    }