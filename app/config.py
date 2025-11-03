from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/uniguide"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Scraping
    scraper_rate_limit_seconds: int = 2
    scraper_max_retries: int = 3

    # Cache
    cache_ttl_seconds: int = 86400  # 24 hours

    # Background Jobs
    refresh_data_cron: str = "0 2 * * *"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env file


@lru_cache()
def get_settings() -> Settings:
    return Settings()
