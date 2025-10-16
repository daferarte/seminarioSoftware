from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, SmallInteger, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class EventStatus(enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(EventStatus))
    total_sessions = Column(SmallInteger)
    faculty_id = Column(Integer)
    created_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 🔹 relaciones
    created_by = relationship("Staff", backref="events")
    registrations = relationship("EventRegistration", back_populates="event")  # 👈 ESTA LÍNEA ES LA CLAVE
