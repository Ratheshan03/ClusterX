from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

from app.database import get_db
from app.models import ScrapingLog
from app.services.cache_service import cache_service

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns the status of the API, database, cache, and last scrape time
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "unknown",
        "cache": "unknown",
        "last_scrape": None,
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"

    # Check cache
    try:
        if cache_service.redis_client:
            cache_service.redis_client.ping()
            health_status["cache"] = "connected"
        else:
            health_status["cache"] = "disabled"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status["cache"] = "disconnected"

    # Get last successful scrape
    try:
        last_log = (
            db.query(ScrapingLog)
            .filter_by(status="success")
            .order_by(ScrapingLog.completed_at.desc())
            .first()
        )
        if last_log:
            health_status["last_scrape"] = last_log.completed_at.isoformat()
    except Exception as e:
        logger.error(f"Error fetching last scrape: {e}")

    return health_status
