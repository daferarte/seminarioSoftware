from sqlalchemy.orm import Session
from app.models.event_registration import EventRegistration

class EventRegistrationRepository:
    def create(self, db: Session, registration: EventRegistration):
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration

    def get_all(self, db: Session):
        return db.query(EventRegistration).all()

    def get_by_id(self, db: Session, reg_id: int):
        return db.query(EventRegistration).filter(EventRegistration.id == reg_id).first()

    def get_existing_registration(self, db: Session, event_id: int, participant_document_id: str):
        """Verifica si un participante ya está inscrito en un evento."""
        return (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.participant_document_id == participant_document_id,
            )
            .first()
        )
