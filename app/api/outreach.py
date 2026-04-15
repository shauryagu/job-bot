"""
Outreach API Router

Handles outreach-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.outreach import Outreach
from app.models.contact import Contact
from app.schemas.outreach import OutreachResponse, OutreachDraftRequest

router = APIRouter()


@router.get("/contacts/{company}")
async def get_contacts_for_company(company: str, db: Session = Depends(get_db)):
    """
    Get contacts for a specific company.

    Args:
        company: Company name
        db: Database session

    Returns:
        List of contacts
    """
    contacts = db.query(Contact).filter(Contact.company == company).all()

    return contacts


@router.post("/generate")
async def generate_outreach_draft(
    request: OutreachDraftRequest,
    db: Session = Depends(get_db),
):
    """
    Generate an outreach draft.

    Args:
        request: Draft generation request
        db: Database session

    Returns:
        Generated draft
    """
    # TODO: Implement LLM-based draft generation
    return {
        "message": "Outreach draft generated",
        "application_id": request.application_id,
        "contact_id": request.contact_id,
        "contact_type": request.contact_type,
        "draft": "Sample outreach message...",
    }


@router.post("/{outreach_id}/send")
async def mark_outreach_sent(outreach_id: int, db: Session = Depends(get_db)):
    """
    Mark an outreach as sent.

    Args:
        outreach_id: Outreach ID
        db: Database session

    Returns:
        Updated outreach
    """
    outreach = db.query(Outreach).filter(Outreach.id == outreach_id).first()

    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")

    # TODO: Mark as sent and update timestamp
    return {"message": "Outreach marked as sent", "outreach_id": outreach_id}