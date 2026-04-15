"""
Profile API Router

Handles profile-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.profile import UserProfile
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(db: Session = Depends(get_db)):
    """
    Get user profile.

    Args:
        db: Database session

    Returns:
        User profile
    """
    # For now, return the first profile (will be updated with auth)
    profile = db.query(UserProfile).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Update user profile.

    Args:
        profile_update: Profile update data
        db: Database session

    Returns:
        Updated profile
    """
    profile = db.query(UserProfile).first()

    if not profile:
        # Create new profile if none exists
        profile = UserProfile(
            full_name=profile_update.full_name,
            email=profile_update.email,
            phone=profile_update.phone,
            linkedin=profile_update.linkedin,
            github=profile_update.github,
        )
        db.add(profile)
    else:
        # Update existing profile
        if profile_update.full_name:
            profile.full_name = profile_update.full_name
        if profile_update.email:
            profile.email = profile_update.email
        if profile_update.phone:
            profile.phone = profile_update.phone
        if profile_update.linkedin:
            profile.linkedin = profile_update.linkedin
        if profile_update.github:
            profile.github = profile_update.github

    db.commit()
    db.refresh(profile)

    return profile