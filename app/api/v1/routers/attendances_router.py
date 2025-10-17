from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])
service = AttendanceService()


# 🔹 Dependencia de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/record")
def record_attendance(data: dict, db: Session = Depends(get_db)):
    """
    Endpoint que recibe el contenido del QR (JSON) y registra automáticamente
    la entrada o salida del participante.
    """
    try:
        result = service.check_in_or_out(db, data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
