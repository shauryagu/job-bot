"""
Pytest Configuration Module

Shared fixtures and configuration for pytest tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.db.base import Base

# Import all models to ensure they're registered with Base
from app.models import job, application, contact, outreach, profile, tracker, company

# Import routers
from app.api import jobs, applications, outreach, tracker, profile, companies

# Create test-specific app without lifespan
test_app = FastAPI()

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
test_app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
test_app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
test_app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
test_app.include_router(tracker.router, prefix="/api/tracker", tags=["tracker"])
test_app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
test_app.include_router(companies.router, prefix="/api/companies", tags=["companies"])

# Add root and health endpoints
@test_app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "status": "running"}

@test_app.get("/health")
async def health_check():
    return {"status": "healthy"}, company


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
    except Exception:
        session.rollback()
        raise
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

    # Override the dependency BEFORE creating the client
    from app.db import session as db_session_module
    test_app.dependency_overrides[db_session_module.get_db] = override_get_db

    # Create client with the override in place
    test_client = TestClient(test_app)

    try:
        yield test_client
    finally:
        # Clean up override
        test_app.dependency_overrides.clear()