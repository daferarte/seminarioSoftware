from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    CC = "CC"
    TI = "TI"
    PASSPORT = "PASSPORT"

class ParticipantBase(BaseModel):
    document_id: str
    document_type: DocumentType
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    career: str
    idnumber: str

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantOut(ParticipantBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
