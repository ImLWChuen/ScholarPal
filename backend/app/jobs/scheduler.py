"""
Scheduled jobs and background change orchestration.
Includes crawler synchronization and freshness audits.
Note: In accordance with Non-negotiable Rule 4, failed retrieval retains the last known record
and flags uncertain freshness; it NEVER marks a scholarship closed.
"""

import logging

logger = logging.getLogger(__name__)


async def audit_freshness_job() -> None:
    """
    Periodic job: Scans active scholarships. If retrieval fails, marks freshness as 'uncertain'
    while keeping the existing record intact.
    """
    logger.info("Executing freshness audit job...")
    # Placeholder for scheduled task implementation


async def trigger_crawler_sync_job() -> None:
    """
    Triggers Scrapy crawler pipeline to collect new and updated portal data.
    """
    logger.info("Executing crawler sync job...")
    # Placeholder for crawler execution
