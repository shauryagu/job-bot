"""
Database Initialization Module

Handles database initialization and migration.
"""

from pathlib import Path
from app.db.session import engine, init_db
from app.db.base import Base
from app.core.logging import logger
from app.models import job, application, contact, outreach, profile, tracker


async def init_database() -> None:
    """
    Initialize the database.

    Creates all tables if they don't exist.
    """
    try:
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

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_database())