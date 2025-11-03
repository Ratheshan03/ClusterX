import logging
from typing import List, Dict, Any
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class DiscoverUniScraper(BaseScraper):
    """Scraper for UK university course data"""

    def __init__(self):
        super().__init__()

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch course data - using sample data for demo"""
        logger.info("Fetching UK university course data")
        return self._get_sample_data()

    def parse_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse data into database format"""
        universities = {}
        courses = []

        for item in raw_data:
            uni_name = item["university_name"]

            if uni_name not in universities:
                universities[uni_name] = {
                    "name": uni_name,
                    "location": item["location"],
                    "website_url": item["website_url"],
                }

            courses.append({
                "university_name": uni_name,
                "name": item["course_name"],
                "subject_area": item["subject_area"],
                "qualification": item["qualification"],
                "duration_years": item["duration_years"],
                "ucas_code": item["ucas_code"],
                "course_url": item["course_url"],
                "year": item.get("year", 2024),
                "entry_requirements": item.get("entry_requirements", []),
            })

        return {"universities": list(universities.values()), "courses": courses}

    def _get_sample_data(self) -> List[Dict[str, Any]]:
        """Sample UK university courses"""
        return [
            {
                "university_name": "University of Oxford",
                "location": "Oxford",
                "website_url": "https://www.ox.ac.uk",
                "course_name": "Computer Science",
                "subject_area": "Computer Science",
                "qualification": "BA",
                "duration_years": 3,
                "ucas_code": "G400",
                "course_url": "https://www.ox.ac.uk/admissions/undergraduate/courses/computer-science",
                "year": 2024,
                "entry_requirements": [
                    {
                        "requirement_type": "A-Level",
                        "typical_offer": "A*AA",
                        "minimum_offer": "A*AA",
                        "subject_requirements": {"required": ["Mathematics"]},
                    }
                ],
            },
            {
                "university_name": "University of Cambridge",
                "location": "Cambridge",
                "website_url": "https://www.cam.ac.uk",
                "course_name": "Computer Science",
                "subject_area": "Computer Science",
                "qualification": "BA",
                "duration_years": 3,
                "ucas_code": "G400",
                "course_url": "https://www.cam.ac.uk/courses/computer-science",
                "year": 2024,
                "entry_requirements": [
                    {
                        "requirement_type": "A-Level",
                        "typical_offer": "A*A*A",
                        "minimum_offer": "A*A*A",
                        "subject_requirements": {"required": ["Mathematics"]},
                    }
                ],
            },
            {
                "university_name": "Imperial College London",
                "location": "London",
                "website_url": "https://www.imperial.ac.uk",
                "course_name": "Computing",
                "subject_area": "Computer Science",
                "qualification": "MEng",
                "duration_years": 4,
                "ucas_code": "G401",
                "course_url": "https://www.imperial.ac.uk/computing",
                "year": 2024,
                "entry_requirements": [
                    {
                        "requirement_type": "A-Level",
                        "typical_offer": "A*A*A",
                        "minimum_offer": "A*A*A",
                        "subject_requirements": {"required": ["Mathematics"]},
                    }
                ],
            },
            {
                "university_name": "University College London",
                "location": "London",
                "website_url": "https://www.ucl.ac.uk",
                "course_name": "Computer Science",
                "subject_area": "Computer Science",
                "qualification": "BSc",
                "duration_years": 3,
                "ucas_code": "G400",
                "course_url": "https://www.ucl.ac.uk/computer-science",
                "year": 2024,
                "entry_requirements": [
                    {
                        "requirement_type": "A-Level",
                        "typical_offer": "A*A*A",
                        "minimum_offer": "A*AA",
                        "subject_requirements": {"required": ["Mathematics"]},
                    }
                ],
            },
            {
                "university_name": "University of Edinburgh",
                "location": "Edinburgh",
                "website_url": "https://www.ed.ac.uk",
                "course_name": "Computer Science",
                "subject_area": "Computer Science",
                "qualification": "BSc",
                "duration_years": 4,
                "ucas_code": "G400",
                "course_url": "https://www.ed.ac.uk/computer-science",
                "year": 2024,
                "entry_requirements": [
                    {
                        "requirement_type": "A-Level",
                        "typical_offer": "A*AA",
                        "minimum_offer": "AAB",
                        "subject_requirements": {"required": ["Mathematics"]},
                    }
                ],
            },
        ]
