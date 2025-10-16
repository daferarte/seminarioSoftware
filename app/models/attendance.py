from sqlalchemy import Column, Integer, TIMESTAMP, func, ForeignKey
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(Integer, ForeignKey("event_registrations.id"))
    session_number = Column(Integer)
    entry_timestamp = Column(TIMESTAMP)
    exit_timestamp = Column(TIMESTAMP)
    scanned_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
