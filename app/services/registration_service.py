from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from app.models.event_registration import EventRegistration
from app.schemas.registration_schema import EventRegistrationCreate
from app.repositories.registration_repository import EventRegistrationRepository


class EventRegistrationService:
    def __init__(self):
        self.repo = EventRegistrationRepository()

    def create_registration(self, db: Session, data: EventRegistrationCreate):
        """Crea un nuevo registro de inscripción de participante a evento."""
        registration = EventRegistration(
            event_id=data.event_id,
            participant_document_id=data.participant_document_id,
            registered_by_staff_id=data.registered_by_staff_id,
            qr_code_sent=data.qr_code_sent or False,
            qr_sent_at=datetime.utcnow() if data.qr_code_sent else None,
            is_paid=data.is_paid if hasattr(data, "is_paid") else False,  # 👈 nuevo campo
        )
        return self.repo.create(db, registration)

    def list_registrations(self, db: Session):
        """Obtiene todas las inscripciones."""
        return self.repo.get_all(db)

    def get_registration(self, db: Session, reg_id: int):
        """Obtiene una inscripción específica por su ID."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
        return reg

    def mark_as_paid(self, db: Session, reg_id: int):
        """Actualiza una inscripción para marcarla como pagada."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        reg.is_paid = True
        db.commit()
        db.refresh(reg)
        return reg

    def mark_as_unpaid(self, db: Session, reg_id: int):
        """Permite revertir el estado de pago si es necesario."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        reg.is_paid = False
        db.commit()
        db.refresh(reg)
        return reg
