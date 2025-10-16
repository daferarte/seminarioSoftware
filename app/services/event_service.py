from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event_schema import EventCreate
from app.repositories.event_repository import EventRepository

class EventService:
    def __init__(self):
        self.repo = EventRepository()

    def create_event(self, db: Session, data: EventCreate):
        event = Event(**data.dict())
        return self.repo.create(db, event)

    def list_events(self, db: Session):
        return self.repo.get_all(db)
