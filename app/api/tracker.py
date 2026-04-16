"""
Tracker API Router

Handles tracker-related API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tracker import TrackerEntry
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException

logger = get_logger(__name__)

router = APIRouter()


@router.post("/sync")
async def sync_tracker(db: Session = Depends(get_db)):
    """
    Sync tracker with Google Sheets.

    Args:
        db: Database session

    Returns:
        Sync results
    """
    # TODO: Implement Google Sheets sync logic
    return {
        "message": "Tracker sync initiated",
        "status": "in_progress",
    }


@router.get("/")
async def get_tracker_data(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get tracker data.

    Args:
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        Tracker data
    """
    try:
        entries = (
            db.query(TrackerEntry)
            .order_by(TrackerEntry.last_touched.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "entries": entries,
            "total": len(entries),
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Failed to get tracker data: {e}")
        raise DatabaseException(f"Database error: {str(e)}")