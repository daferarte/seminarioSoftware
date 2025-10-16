from sqlalchemy.orm import Session
from app.models.event_registration import EventRegistration

class EventRegistrationRepository:
    def get_all(self, db: Session):
        return db.query(EventRegistration).all()

    def get_by_id(self, db: Session, reg_id: int):
        return db.query(EventRegistration).filter(EventRegistration.id == reg_id).first()

    def create(self, db: Session, registration: EventRegistration):
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
