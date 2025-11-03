from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class EntryRequirement(Base):
    __tablename__ = "entry_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_type = Column(String)  # e.g., A-Level, IB, BTEC
    typical_offer = Column(String)  # e.g., AAA, 38 points
    minimum_offer = Column(String)
    subject_requirements = Column(JSONB)  # JSON object for specific subject needs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="entry_requirements")
