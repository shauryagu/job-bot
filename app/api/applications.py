"""
Applications API Router

Handles application-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.models.application import Application, ApplicationStage
from app.models.job import JobNormalized
from app.schemas.applications import ApplicationResponse, ApplicationCreate, ApplicationStatusUpdate
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get all applications.

    Args:
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        List of applications
    """
    try:
        applications = (
            db.query(Application)
            .order_by(Application.date_applied.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return applications
    except Exception as e:
        logger.error(f"Failed to get applications: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    """
    Get a specific application by ID.

    Args:
        application_id: Application ID
        db: Database session

    Returns:
        Application details
    """
    try:
        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        return application
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get application {application_id}: {e}")
        raise DatabaseException(f"Database error: {str(e)}")


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new application.

    Args:
        application: Application data
        db: Database session

    Returns:
        Created application
    """
    try:
        # Validate job exists
        job = db.query(JobNormalized).filter(JobNormalized.id == application.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Create application with proper defaults
        new_application = Application(
            normalized_job_id=application.job_id,
            company=application.company,
            role=application.role,
            application_url=job.url if hasattr(job, 'url') else None,
            source=job.source if hasattr(job, 'source') else None,
            date_found=job.created_at if hasattr(job, 'created_at') else datetime.utcnow(),
            date_applied=datetime.utcnow(),
            resume_version=application.resume_version,
            notes=application.notes,
            stage=ApplicationStage.APPLIED,
            last_touched=datetime.utcnow(),
        )

        db.add(new_application)
        db.commit()
        db.refresh(new_application)

        logger.info(f"Created application for job {application.job_id}")
        return new_application

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create application")


@router.put("/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Update application status.

    Args:
        application_id: Application ID
        status_update: Status update data
        db: Database session

    Returns:
        Updated application
    """
    try:
        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        application.stage = status_update.stage
        application.next_action = status_update.next_action
        application.follow_up_due = status_update.follow_up_due
        application.last_touched = datetime.utcnow()

        db.commit()

        logger.info(f"Updated status for application {application_id}")
        return {"message": "Application status updated successfully", "application_id": application_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application status {application_id}: {e}")
        db.rollback()
        raise DatabaseException(f"Database error: {str(e)}")