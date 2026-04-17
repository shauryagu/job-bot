"""
Pytest Configuration Module

Shared fixtures and configuration for pytest tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from main import app
from app.db.base import Base
# Import model classes to register them with SQLAlchemy Base metadata
from app.models.job import JobRaw, JobNormalized
from app.models.application import Application
from app.models.profile import UserProfile
from app.models.tracker import TrackerEntry
from app.models.contact import Contact
from app.models.outreach import Outreach


# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a test database session.

    Yields:
        Database session
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client for FastAPI with database session.

    Args:
        db_session: Database session fixture

    Yields:
        Test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override the dependency
    from app.db import session as db_session_module
    app.dependency_overrides[db_session_module.get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        # Clean up override
        app.dependency_overrides.clear()