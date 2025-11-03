from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time
import logging
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self):
        self.rate_limit = settings.scraper_rate_limit_seconds
        self.max_retries = settings.scraper_max_retries
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Ensure rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the source"""
        pass

    @abstractmethod
    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw data into structured format"""
        pass
