"""
Manual Tracker Sync Script

Script to manually trigger tracker synchronization with Google Sheets.
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
    """Main function to sync tracker."""
    logger.info("Starting tracker sync...")

    # TODO: Implement tracker sync logic
    logger.info("Tracker sync not yet implemented")

    logger.info("Tracker sync completed")


if __name__ == "__main__":
    asyncio.run(main())