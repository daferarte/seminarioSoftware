from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.attendance_schema import AttendanceCreate, AttendanceOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])
service = AttendanceService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AttendanceOut)
def create_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    return service.create_attendance(db, data)

@router.get("/", response_model=list[AttendanceOut])
def list_attendance(db: Session = Depends(get_db)):
    return service.list_attendance(db)

@router.get("/{attendance_id}", response_model=AttendanceOut)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    att = service.get_attendance(db, attendance_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return att
