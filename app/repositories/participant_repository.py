from sqlalchemy.orm import Session
from app.models.participant import Participant

class ParticipantRepository:
    def get_all(self, db: Session):
        return db.query(Participant).all()

    def create(self, db: Session, participant: Participant):
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant
