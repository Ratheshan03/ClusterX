from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    subject_area = Column(String, index=True)
    qualification = Column(String)  # e.g., BSc, MEng, BA
    duration_years = Column(Integer)
    ucas_code = Column(String, unique=True)
    course_url = Column(String)
    year = Column(Integer, index=True)  # Academic year
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    university = relationship("University", back_populates="courses")
    entry_requirements = relationship("EntryRequirement", back_populates="course", cascade="all, delete-orphan")
