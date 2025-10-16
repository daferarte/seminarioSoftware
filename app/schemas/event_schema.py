from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class EventStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[EventStatus] = EventStatus.DRAFT
    total_sessions: Optional[int] = 1
    faculty_id: Optional[int] = None
    created_by_staff_id: int

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
