from sqlalchemy.orm import Session
from app.models.event import Event

class EventRepository:
    def get_all(self, db: Session):
        return db.query(Event).all()

    def create(self, db: Session, event: Event):
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
