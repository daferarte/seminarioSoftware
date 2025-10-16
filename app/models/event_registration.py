from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    participant_document_id = Column(String(20), ForeignKey("participants.document_id"))
    registered_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    qr_code_sent = Column(Boolean, default=False)
    qr_sent_at = Column(TIMESTAMP)
    registration_date = Column(TIMESTAMP, server_default=func.now())
    
    is_paid = Column(Boolean, default=False, nullable=False)

    # 🔹 relaciones
    event = relationship("Event", back_populates="registrations")
    participant = relationship("Participant", backref="registrations")
    staff = relationship("Staff", backref="registrations")
