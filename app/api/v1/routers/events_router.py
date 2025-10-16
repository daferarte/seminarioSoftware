from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.event_schema import EventCreate, EventOut
from app.services.event_service import EventService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])
service = EventService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventOut)
# def create_event(data: EventCreate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    return service.create_event(db, data)

@router.get("/", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return service.list_events(db)
