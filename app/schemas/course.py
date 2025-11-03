from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from app.schemas.entry_requirement import EntryRequirement


class CourseBase(BaseModel):
    name: str
    subject_area: Optional[str] = None
    qualification: Optional[str] = None
    duration_years: Optional[int] = None
    ucas_code: Optional[str] = None
    course_url: Optional[str] = None
    year: Optional[int] = None


class Course(CourseBase):
    id: UUID4
    university_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseWithDetails(Course):
    university_name: str
    entry_requirements: List[EntryRequirement] = []

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: List[CourseWithDetails]


class CourseResponse(CourseWithDetails):
    pass
