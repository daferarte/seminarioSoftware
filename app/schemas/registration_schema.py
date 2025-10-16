from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventRegistrationBase(BaseModel):
    event_id: int
    participant_document_id: str
    registered_by_staff_id: int
    qr_code_sent: Optional[bool] = False
    is_paid: Optional[bool] = False 

class EventRegistrationCreate(EventRegistrationBase):
    pass

class EventRegistrationOut(EventRegistrationBase):
    id: int
    qr_sent_at: Optional[datetime]
    registration_date: datetime

    class Config:
        orm_mode = True
