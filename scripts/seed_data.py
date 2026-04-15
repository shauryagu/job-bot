"""
Seed Data Script

Script to seed the database with initial data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.profile import UserProfile

logger = setup_logging()


def seed_user_profile():
    """Seed user profile data."""
    db = SessionLocal()

    try:
        # Check if profile already exists
        existing_profile = db.query(UserProfile).first()

        if existing_profile:
            logger.info("User profile already exists, skipping seed")
            return

        # Create sample user profile
        profile = UserProfile(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-123-4567",
            city="New York",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe",
            portfolio="https://johndoe.dev",
            visa_status="US Citizen",
        )

        db.add(profile)
        db.commit()

        logger.info("User profile seeded successfully")

    except Exception as e:
        logger.error(f"Error seeding user profile: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """Main function to seed data."""
    logger.info("Starting data seeding...")

    seed_user_profile()

    logger.info("Data seeding completed")


if __name__ == "__main__":
    asyncio.run(main())