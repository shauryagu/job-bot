"""
Profile Models Module

Defines database models for user profile data.
"""

from sqlalchemy import Column, String, Integer, Text
from app.db.base import BaseModel


class UserProfile(BaseModel):
    """
    User profile model.

    Stores user personal information and preferences.
    """

    __tablename__ = "user_profile"

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    city = Column(String)
    linkedin = Column(String)
    github = Column(String)
    portfolio = Column(String)
    visa_status = Column(String)
    work_authorization_answers = Column(Text)  # JSON string
    resume_variants = Column(Text)  # JSON string for multiple resume versions
    common_answers_json = Column(Text)  # JSON string for common application answers

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name={self.full_name}, email={self.email})>"