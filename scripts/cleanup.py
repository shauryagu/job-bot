"""
Cleanup Script

Script to clean up old data and perform maintenance tasks.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.job import JobRaw, JobNormalized, JobStatus

logger = setup_logging()


def cleanup_old_jobs(days: int = 30):
    """
    Clean up jobs older than specified days.

    Args:
        days: Number of days to keep
    """
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Archive old jobs
        old_jobs = (
            db.query(JobNormalized)
            .filter(
                JobNormalized.created_at < cutoff_date,
                JobNormalized.status.in_([JobStatus.REJECTED, JobStatus.ARCHIVED]),
            )
            .all()
        )

        count = len(old_jobs)

        for job in old_jobs:
            job.status = JobStatus.ARCHIVED

        db.commit()

        logger.info(f"Archived {count} old jobs")

    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {e}")
        db.rollback()
    finally:
        db.close()


def cleanup_cache():
    """Clean up cache files."""
    import os

    cache_dir = Path("data/cache")

    if not cache_dir.exists():
        logger.info("Cache directory does not exist")
        return

    # Get all cache files
    cache_files = list(cache_dir.glob("*"))

    count = len(cache_files)

    # Delete cache files
    for file in cache_files:
        if file.is_file():
            file.unlink()

    logger.info(f"Cleaned up {count} cache files")


async def main():
    """Main function to perform cleanup."""
    logger.info("Starting cleanup...")

    cleanup_old_jobs(days=30)
    cleanup_cache()

    logger.info("Cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())