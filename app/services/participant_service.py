import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.participant import Participant
from app.repositories.participant_repository import ParticipantRepository

class ParticipantService:
    def __init__(self):
        self.repo = ParticipantRepository()

    def create_participant(self, db: Session, data):
        existing = self.repo.get_by_document_id(db, data.document_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Participant with document {data.document_id} already exists."
            )
        participant = Participant(**data.dict())
        return self.repo.create(db, participant)

    def list_participants(self, db: Session):
        return self.repo.get_all(db)

    def get_participant(self, db: Session, participant_id: str):
        return self.repo.get_by_document_id(db, participant_id)

    def import_from_excel(self, db: Session, file: UploadFile):
        """Importa múltiples participantes desde un archivo Excel (.xlsx)."""
        try:
            df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al leer el archivo Excel: {str(e)}")

        required_columns = {
            "document_id",
            "document_type",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "career",
            "idnumber",
        }

        # Validar que las columnas sean correctas
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo Excel debe contener las columnas: {', '.join(required_columns)}"
            )

        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            existing = self.repo.get_by_document_id(db, str(row["document_id"]))
            if existing:
                skipped += 1
                continue

            participant = Participant(
                document_id=str(row["document_id"]),
                document_type=str(row["document_type"]),
                first_name=str(row["first_name"]),
                last_name=str(row["last_name"]),
                email=str(row["email"]),
                phone_number=str(row["phone_number"]),
                career=str(row["career"]),
                idnumber=str(row["idnumber"]),
            )

            db.add(participant)
            inserted += 1

        db.commit()

        return {
            "status": "success",
            "inserted": inserted,
            "skipped": skipped,
            "message": f"Se importaron {inserted} participantes. Se omitieron {skipped} duplicados."
        }
