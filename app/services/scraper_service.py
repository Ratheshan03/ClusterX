import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.scrapers.discover_uni import DiscoverUniScraper
from app.models import University, Course, EntryRequirement, ScrapingLog
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for managing data scraping and storage"""

    def __init__(self, db: Session):
        self.db = db
        self.scraper = DiscoverUniScraper()

    async def refresh_data(self, source: str = "discover_uni") -> dict:
        """
        Fetch fresh data from source and update database
        """
        log = ScrapingLog(source=source, status="in_progress")
        self.db.add(log)
        self.db.commit()

        try:
            # Fetch data
            logger.info(f"Starting data refresh from {source}")
            raw_data = await self.scraper.fetch_data()

            # Parse data
            parsed_data = self.scraper.parse_data(raw_data)

            # Store universities
            universities_map = {}
            for uni_data in parsed_data["universities"]:
                university = self._upsert_university(uni_data)
                universities_map[university.name] = university

            # Store courses and requirements
            courses_created = 0
            for course_data in parsed_data["courses"]:
                university = universities_map.get(course_data["university_name"])
                if university:
                    self._upsert_course(course_data, university.id)
                    courses_created += 1

            # Update log
            log.status = "success"
            log.records_fetched = courses_created
            log.completed_at = datetime.utcnow()
            self.db.commit()

            # Clear cache after successful refresh
            cache_service.clear_pattern("courses:*")
            cache_service.clear_pattern("universities:*")

            logger.info(
                f"Data refresh completed. {len(universities_map)} universities, {courses_created} courses"
            )

            return {
                "status": "success",
                "universities_count": len(universities_map),
                "courses_count": courses_created,
            }

        except Exception as e:
            logger.error(f"Data refresh failed: {e}")
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def _upsert_university(self, uni_data: dict) -> University:
        """Insert or update university"""
        university = (
            self.db.query(University).filter_by(name=uni_data["name"]).first()
        )

        if university:
            # Update existing
            university.location = uni_data.get("location")
            university.website_url = uni_data.get("website_url")
        else:
            # Create new
            university = University(**uni_data)
            self.db.add(university)

        try:
            self.db.commit()
            self.db.refresh(university)
        except IntegrityError:
            self.db.rollback()
            university = (
                self.db.query(University).filter_by(name=uni_data["name"]).first()
            )

        return university

    def _upsert_course(self, course_data: dict, university_id):
        """Insert or update course"""
        # Remove university_name from course_data as we have university_id
        course_data = course_data.copy()
        course_data.pop("university_name", None)
        entry_requirements_data = course_data.pop("entry_requirements", [])

        # Check if course exists
        course = None
        if course_data.get("ucas_code"):
            course = (
                self.db.query(Course)
                .filter_by(ucas_code=course_data["ucas_code"])
                .first()
            )

        if course:
            # Update existing course
            for key, value in course_data.items():
                setattr(course, key, value)
            course.university_id = university_id
        else:
            # Create new course
            course = Course(university_id=university_id, **course_data)
            self.db.add(course)

        try:
            self.db.commit()
            self.db.refresh(course)

            # Delete old entry requirements and add new ones
            self.db.query(EntryRequirement).filter_by(course_id=course.id).delete()

            # Add entry requirements
            for req_data in entry_requirements_data:
                entry_req = EntryRequirement(course_id=course.id, **req_data)
                self.db.add(entry_req)

            self.db.commit()

        except IntegrityError as e:
            logger.warning(f"IntegrityError inserting course: {e}")
            self.db.rollback()
