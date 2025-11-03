from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String)  # e.g., discover_uni, ucas
    status = Column(String)  # success, failed, partial
    records_fetched = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
