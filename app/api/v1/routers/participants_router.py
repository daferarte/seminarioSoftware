from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.participant_schema import ParticipantCreate, ParticipantOut
from app.services.participant_service import ParticipantService

router = APIRouter(prefix="/participants", tags=["Participants"])
service = ParticipantService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ParticipantOut)
def create_participant(data: ParticipantCreate, db: Session = Depends(get_db)):
    """Crea un nuevo participante individualmente desde JSON."""
    return service.create_participant(db, data)

@router.get("/", response_model=list[ParticipantOut])
def list_participants(db: Session = Depends(get_db)):
    """Lista todos los participantes registrados en la base de datos."""
    return service.list_participants(db)

# 👇 NUEVO ENDPOINT PARA IMPORTAR EXCEL
@router.post("/import-excel")
def import_participants_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa múltiples participantes desde un archivo Excel (.xlsx).
    El archivo debe contener las columnas:
    document_id, document_type, first_name, last_name, email, phone_number, career, idnumber.
    """
    return service.import_from_excel(db, file)
