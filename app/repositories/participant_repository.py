from sqlalchemy.orm import Session
from app.models.participant import Participant

class ParticipantRepository:
    def create(self, db: Session, participant: Participant):
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    def get_all(self, db: Session):
        return db.query(Participant).all()

    def get_by_id(self, db: Session, participant_id: int):
        return db.query(Participant).filter(Participant.document_id == participant_id).first()

    # ✅ Nuevo método para evitar duplicados
    def get_by_document_id(self, db: Session, document_id: str):
        """Busca un participante por su documento."""
        return db.query(Participant).filter(Participant.document_id == document_id).first()
