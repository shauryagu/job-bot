"""
Applications API Router

Handles application-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.application import Application
from app.schemas.applications import ApplicationResponse, ApplicationCreate, ApplicationStatusUpdate

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
    applications = (
        db.query(Application)
        .order_by(Application.date_applied.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return applications


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
    application = (
        db.query(Application).filter(Application.id == application_id).first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


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
    # TODO: Implement application creation logic
    new_application = Application(
        normalized_job_id=application.job_id,
        company=application.company,
        role=application.role,
        resume_version=application.resume_version,
        notes=application.notes,
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


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
    application = (
        db.query(Application).filter(Application.id == application_id).first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.stage = status_update.stage
    application.next_action = status_update.next_action
    application.follow_up_due = status_update.follow_up_due

    db.commit()

    return {"message": "Application status updated successfully", "application_id": application_id}