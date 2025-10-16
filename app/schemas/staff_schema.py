from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class StaffBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    role: Optional[str] = None
    is_active: Optional[bool] = True

class StaffCreate(StaffBase):
    password: str

class StaffOut(StaffBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
