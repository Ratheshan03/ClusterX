import logging
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.models import Course, University, EntryRequirement
from app.schemas.course import CourseWithDetails
from app.services.cache_service import cache_service
import hashlib
import json

logger = logging.getLogger(__name__)


class CourseService:
    """Service for course queries"""

    def __init__(self, db: Session):
        self.db = db

    def get_courses(
        self,
        university: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
        qualification: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[CourseWithDetails], int]:
        """
        Get courses with filters
        Returns tuple of (courses, total_count)
        """
        # Generate cache key
        cache_key = self._generate_cache_key(
            university, subject, year, qualification, limit, offset
        )

        # Try cache first
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached["results"], cached["total"]

        # Build query
        query = (
            self.db.query(Course)
            .join(University)
            .options(joinedload(Course.entry_requirements))
        )

        # Apply filters
        if university:
            query = query.filter(
                func.lower(University.name).contains(university.lower())
            )

        if subject:
            query = query.filter(
                func.lower(Course.subject_area).contains(subject.lower())
            )

        if year:
            query = query.filter(Course.year == year)

        if qualification:
            query = query.filter(
                func.lower(Course.qualification) == qualification.lower()
            )

        # Get total count
        total = query.count()

        # Get paginated results
        courses = query.order_by(Course.created_at.desc()).limit(limit).offset(offset).all()

        # Convert to schema with university name
        results = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "university_id": course.university_id,
                "name": course.name,
                "subject_area": course.subject_area,
                "qualification": course.qualification,
                "duration_years": course.duration_years,
                "ucas_code": course.ucas_code,
                "course_url": course.course_url,
                "year": course.year,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
                "university_name": course.university.name,
                "entry_requirements": course.entry_requirements,
            }
            results.append(CourseWithDetails(**course_dict))

        # Cache results
        cache_service.set(cache_key, {"results": [r.dict() for r in results], "total": total})

        return results, total

    def _generate_cache_key(
        self,
        university: Optional[str],
        subject: Optional[str],
        year: Optional[int],
        qualification: Optional[str],
        limit: int,
        offset: int,
    ) -> str:
        """Generate cache key from query parameters"""
        params = {
            "university": university,
            "subject": subject,
            "year": year,
            "qualification": qualification,
            "limit": limit,
            "offset": offset,
        }
        params_str = json.dumps(params, sort_keys=True)
        hash_key = hashlib.md5(params_str.encode()).hexdigest()
        return f"courses:{hash_key}"
