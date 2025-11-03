from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import University
from app.schemas.university import UniversityResponse

router = APIRouter(prefix="/universities", tags=["universities"])
logger = logging.getLogger(__name__)


@router.get("", response_model=UniversityResponse)
async def get_universities(db: Session = Depends(get_db)):
    """
    Get all universities in the database
    """
    try:
        universities = db.query(University).order_by(University.name).all()
        total = len(universities)

        return UniversityResponse(total=total, results=universities)

    except Exception as e:
        logger.error(f"Error fetching universities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
