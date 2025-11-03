import redis
import json
import logging
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID and datetime objects"""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    """Redis caching service"""

    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.redis_url, decode_responses=True
            )
            self.ttl = settings.cache_ttl_seconds
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}. Cache disabled.")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False

        try:
            ttl = ttl or self.ttl
            # Use custom encoder to handle UUID and datetime objects
            json_str = json.dumps(value, cls=CustomJSONEncoder)
            self.redis_client.setex(key, ttl, json_str)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return False

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False


# Singleton instance
cache_service = CacheService()
