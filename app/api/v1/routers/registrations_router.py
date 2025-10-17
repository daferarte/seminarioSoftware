from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.registration_schema import EventRegistrationCreate, EventRegistrationOut
from app.services.registration_service import EventRegistrationService

router = APIRouter(prefix="/registrations", tags=["Registrations"])
service = EventRegistrationService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# 📦 CRUD BASE
# ======================================================
@router.post("/", response_model=EventRegistrationOut)
def create_registration(data: EventRegistrationCreate, db: Session = Depends(get_db)):
    return service.create_registration(db, data)

@router.get("/", response_model=list[EventRegistrationOut])
def list_registrations(db: Session = Depends(get_db)):
    return service.list_registrations(db)

@router.get("/{registration_id}", response_model=EventRegistrationOut)
def get_registration(registration_id: int, db: Session = Depends(get_db)):
    reg = service.get_registration(db, registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg

@router.put("/{registration_id}/pay", response_model=EventRegistrationOut)
def mark_as_paid(registration_id: int, db: Session = Depends(get_db)):
    """Marca una inscripción como pagada."""
    return service.mark_as_paid(db, registration_id)

@router.put("/{registration_id}/unpay", response_model=EventRegistrationOut)
def mark_as_unpaid(registration_id: int, db: Session = Depends(get_db)):
    """Revierte una inscripción a estado no pagado."""
    return service.mark_as_unpaid(db, registration_id)

@router.post("/import-excel")
def import_event_registrations(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importa múltiples registros desde Excel."""
    return service.import_from_excel(db, file)

# ======================================================
# 🎫 GENERAR CÓDIGO QR
# ======================================================
@router.get("/{registration_id}/generate-qr")
def generate_qr(registration_id: int, db: Session = Depends(get_db)):
    """
    Genera un código QR seguro (PNG en base64) con firma HMAC.
    Contiene los datos del evento y participante.
    """
    result = service.generate_qr_for_registration(db, registration_id)
    if not result:
        raise HTTPException(status_code=404, detail="Registration not found")
    return result
