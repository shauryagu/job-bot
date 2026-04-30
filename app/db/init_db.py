"""
Database Initialization Module

Handles database initialization, health checks, and seed data.
"""

from pathlib import Path
from sqlalchemy import text
from app.db.session import engine, SessionLocal, init_db
from app.db.base import Base
from app.core.logging import logger
from app.core.config import settings
from app.models import job, application, contact, outreach, profile, tracker, company


async def check_database_health() -> bool:
    """
    Check database health.

    Returns:
        True if database is healthy, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def seed_development_data() -> None:
    """
    Seed development data.

    Creates test data for development environment.
    """
    if settings.environment != "development":
        logger.info("Skipping seed data - not in development mode")
        return

    try:
        db = SessionLocal()

        # Check if data already exists
        existing_profile = db.query(profile.UserProfile).first()
        if existing_profile:
            logger.info("Development data already exists, skipping seed")
            db.close()
            return

        # Create test user profile
        test_profile = profile.UserProfile(
            full_name="Test User",
            email="test@example.com",
            phone="555-1234",
            city="New York",
            linkedin="https://linkedin.com/in/test",
            github="https://github.com/test",
        )
        db.add(test_profile)

        # Create test job
        test_job = job.JobNormalized(
            company="Test Company",
            role="Software Engineer",
            priority_score=85.0,
            status=job.JobStatus.NEW,
        )
        db.add(test_job)

        # Create test application
        test_application = application.Application(
            company="Test Company",
            role="Software Engineer",
            stage=application.ApplicationStage.APPLIED,
            date_applied=None,
        )
        db.add(test_application)

        db.commit()
        db.close()

        logger.info("Development data seeded successfully")

    except Exception as e:
        logger.error(f"Failed to seed development data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise


async def init_database() -> None:
    """
    Initialize the database.

    Creates all tables if they don't exist and seeds development data.
    """
    try:
        # Check database health first
        if not await check_database_health():
            raise Exception("Database health check failed")

        # Initialize database connection
        init_db()

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database tables created successfully")

        # Create data directories
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        database_dir = data_dir / "database"
        database_dir.mkdir(exist_ok=True)

        cache_dir = data_dir / "cache"
        cache_dir.mkdir(exist_ok=True)

        exports_dir = data_dir / "exports"
        exports_dir.mkdir(exist_ok=True)

        uploads_dir = data_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)

        logger.info("Data directories created successfully")

        # Seed development data
        await seed_development_data()

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_database())