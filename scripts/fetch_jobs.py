"""
Manual Job Fetch Script

Script to manually trigger job fetching from configured sources.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.core.config import settings

logger = setup_logging()


async def main():
    """Main function to fetch jobs."""
    logger.info("Starting manual job fetch...")

    # TODO: Implement job fetching logic
    logger.info("Job fetching not yet implemented")

    logger.info("Job fetch completed")


if __name__ == "__main__":
    asyncio.run(main())