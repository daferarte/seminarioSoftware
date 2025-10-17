from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(Integer, ForeignKey("event_registrations.id"), nullable=False)
    participant_document_id = Column(String(50), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="NONE")  # NONE, CHECKED_IN, CHECKED_OUT
    verified_by = Column(Integer, ForeignKey("staff.id"), nullable=True)

    registration = relationship("EventRegistration", backref="attendances")
    event = relationship("Event", backref="attendances")
