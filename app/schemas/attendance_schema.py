from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceBase(BaseModel):
    registration_id: int
    session_number: int
    scanned_by_staff_id: int

class AttendanceCreate(AttendanceBase):
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None

class AttendanceOut(AttendanceBase):
    id: int
    entry_timestamp: Optional[datetime]
    exit_timestamp: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True
