from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.staff_schema import StaffCreate, StaffOut
from app.services.staff_service import StaffService

router = APIRouter(prefix="/staff", tags=["Staff"])
service = StaffService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=StaffOut)
def create_staff(data: StaffCreate, db: Session = Depends(get_db)):
    return service.create_staff(db, data)

@router.get("/", response_model=list[StaffOut])
def list_staff(db: Session = Depends(get_db)):
    return service.list_staff(db)
