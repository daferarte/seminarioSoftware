from sqlalchemy import Column, String, Integer, Enum, TIMESTAMP, func, SmallInteger
from app.core.database import Base
import enum

class DocumentType(enum.Enum):
    CC = "CC"
    TI = "TI"
    PASSPORT = "PASSPORT"

class Participant(Base):
    __tablename__ = "participants"

    document_id = Column(String(20), primary_key=True)
    document_type = Column(Enum(DocumentType))
    first_name = Column(String(150))
    last_name = Column(String(150))
    email = Column(String(255))
    phone_number = Column(String(20))
    career = Column(String(150))
    idnumber = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
