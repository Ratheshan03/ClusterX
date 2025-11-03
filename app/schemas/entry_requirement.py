from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class EntryRequirementBase(BaseModel):
    requirement_type: str
    typical_offer: Optional[str] = None
    minimum_offer: Optional[str] = None
    subject_requirements: Optional[Dict[str, Any]] = None


class EntryRequirement(EntryRequirementBase):
    id: UUID4
    course_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
