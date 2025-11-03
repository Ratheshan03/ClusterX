from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class UniversityBase(BaseModel):
    name: str
    location: Optional[str] = None
    website_url: Optional[str] = None


class University(UniversityBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UniversityResponse(BaseModel):
    total: int
    results: list[University]
