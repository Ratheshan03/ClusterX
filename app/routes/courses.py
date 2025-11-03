from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.schemas.course import CourseListResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])
logger = logging.getLogger(__name__)


@router.get("", response_model=CourseListResponse)
async def get_courses(
    university: Optional[str] = Query(
        None, description="Filter by university name (case-insensitive)"
    ),
    subject: Optional[str] = Query(
        None, description="Filter by subject area (case-insensitive)"
    ),
    year: Optional[int] = Query(None, description="Filter by academic year"),
    qualification: Optional[str] = Query(
        None, description="Filter by qualification type (e.g., BSc, MEng)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
):
    """
    Get courses with optional filters:
    - **university**: Filter by university name (partial match)
    - **subject**: Filter by subject area (partial match)
    - **year**: Filter by academic year
    - **qualification**: Filter by qualification type
    - **limit**: Maximum number of results (1-100, default 50)
    - **offset**: Pagination offset (default 0)
    """
    try:
        service = CourseService(db)
        courses, total = service.get_courses(
            university=university,
            subject=subject,
            year=year,
            qualification=qualification,
            limit=limit,
            offset=offset,
        )

        return CourseListResponse(
            total=total, limit=limit, offset=offset, results=courses
        )

    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh")
async def trigger_refresh(
    source: str = Query("discover_uni", description="Data source to refresh"),
    db: Session = Depends(get_db),
):
    """
    Trigger manual data refresh from the specified source.
    This will fetch fresh data and update the database.
    """
    try:
        from app.services.scraper_service import ScraperService

        service = ScraperService(db)
        result = await service.refresh_data(source=source)

        return {
            "message": "Data refresh completed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        raise HTTPException(status_code=500, detail=f"Data refresh failed: {str(e)}")
