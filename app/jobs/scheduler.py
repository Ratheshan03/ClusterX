from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import asyncio

from app.database import SessionLocal
from app.services.scraper_service import ScraperService

logger = logging.getLogger(__name__)
scheduler = None


def refresh_data_job():
    """Background job to refresh data from sources"""
    logger.info("Starting scheduled data refresh job...")

    db = SessionLocal()
    try:
        service = ScraperService(db)

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.refresh_data())
        loop.close()

        logger.info(f"Scheduled data refresh completed: {result}")

    except Exception as e:
        logger.error(f"Scheduled data refresh failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    global scheduler

    if scheduler is not None:
        logger.warning("Scheduler already running")
        return

    scheduler = BackgroundScheduler()

    # Add daily refresh job at 2 AM UTC
    scheduler.add_job(
        refresh_data_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_refresh",
        name="Daily data refresh",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Background scheduler started - daily refresh at 2 AM UTC")


def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler

    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background scheduler stopped")
