from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status, UploadFile
import pandas as pd
import qrcode
import base64
import io
import hmac
import hashlib
import json
import os

from app.models.event_registration import EventRegistration
from app.schemas.registration_schema import EventRegistrationCreate
from app.repositories.registration_repository import EventRegistrationRepository


class EventRegistrationService:
    def __init__(self):
        self.repo = EventRegistrationRepository()

    # =========================
    # CRUD PRINCIPAL
    # =========================
    def create_registration(self, db: Session, data: EventRegistrationCreate):
        """Crea un nuevo registro de inscripción de participante a evento."""
        registration = EventRegistration(
            event_id=data.event_id,
            participant_document_id=data.participant_document_id,
            registered_by_staff_id=data.registered_by_staff_id,
            qr_code_sent=data.qr_code_sent or False,
            qr_sent_at=datetime.utcnow() if data.qr_code_sent else None,
            is_paid=getattr(data, "is_paid", False),
        )
        return self.repo.create(db, registration)

    def list_registrations(self, db: Session):
        """Obtiene todas las inscripciones."""
        return self.repo.get_all(db)

    def get_registration(self, db: Session, reg_id: int):
        """Obtiene una inscripción específica por su ID."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
        return reg

    def mark_as_paid(self, db: Session, reg_id: int):
        """Marca una inscripción como pagada."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        reg.is_paid = True
        db.commit()
        db.refresh(reg)
        return reg

    def mark_as_unpaid(self, db: Session, reg_id: int):
        """Revertir el estado de pago de una inscripción."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

        reg.is_paid = False
        db.commit()
        db.refresh(reg)
        return reg

    # =========================
    # IMPORTAR DESDE EXCEL
    # =========================
    def import_from_excel(self, db: Session, file: UploadFile):
        """Importa múltiples registros de inscripción desde un archivo Excel (.xlsx)."""
        try:
            df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al leer el archivo Excel: {str(e)}"
            )

        required_columns = {
            "event_id",
            "participant_document_id",
            "registered_by_staff_id",
            "qr_code_sent",
            "is_paid",
        }

        # Validar columnas
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo Excel debe contener las columnas: {', '.join(required_columns)}"
            )

        def parse_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value != 0
            if isinstance(value, str):
                return value.strip().lower() in ["true", "1", "yes", "si", "sí"]
            return False

        inserted, skipped = 0, 0

        for _, row in df.iterrows():
            try:
                event_id = int(row["event_id"])
                participant_id = str(row["participant_document_id"])
                staff_id = int(row["registered_by_staff_id"])
                qr_sent = parse_bool(row["qr_code_sent"])
                is_paid = parse_bool(row["is_paid"])
            except Exception as e:
                skipped += 1
                print(f"⚠️ Error al procesar fila: {row.to_dict()} → {e}")
                continue

            existing = self.repo.get_existing_registration(
                db,
                event_id=event_id,
                participant_document_id=participant_id,
            )
            if existing:
                skipped += 1
                continue

            registration = EventRegistration(
                event_id=event_id,
                participant_document_id=participant_id,
                registered_by_staff_id=staff_id,
                qr_code_sent=qr_sent,
                qr_sent_at=datetime.utcnow() if qr_sent else None,
                is_paid=is_paid,
            )

            db.add(registration)
            inserted += 1

        db.commit()

        return {
            "status": "success",
            "inserted": inserted,
            "skipped": skipped,
            "message": f"✅ Se importaron {inserted} inscripciones. Se omitieron {skipped} duplicadas o con errores."
        }

    # =========================
    # GENERAR Y GUARDAR QR
    # =========================
    def generate_qr_for_registration(self, db: Session, reg_id: int):
        """Genera un QR firmado, lo guarda como PNG en disco y lo devuelve en base64."""
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        event = getattr(reg, "event", None)
        participant = getattr(reg, "participant", None)

        # 🔸 Datos para el QR
        payload = {
            "registration_id": reg.id,
            "event_id": reg.event_id,
            "participant_document_id": reg.participant_document_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 🔒 Firma HMAC (clave configurable)
        secret_key = b"ucc-seminario-secret-key"
        signature = hmac.new(
            secret_key,
            json.dumps(payload, sort_keys=True).encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        payload["signature"] = signature

        # 🔲 Generar QR
        qr_data = json.dumps(payload)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 🧭 Ruta del archivo
        event_name = (event.name if event else f"evento_{reg.event_id}").replace(" ", "_")
        save_dir = os.path.join("app", "static", "qrs", event_name)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{reg.participant_document_id}.png"
        file_path = os.path.join(save_dir, filename)

        # 🖼 Guardar en disco
        img.save(file_path)

        # 🔁 Convertir también a base64
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        base64_png = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()

        return {
            "status": "success",
            "message": "QR generado y guardado correctamente",
            "registration_id": reg.id,
            "event": event.name if event else f"Evento {reg.event_id}",
            "participant": (
                f"{participant.first_name} {participant.last_name}"
                if participant else reg.participant_document_id
            ),
            "qr_image_path": file_path,
            "qr_image_base64": f"data:image/png;base64,{base64_png}",
        }
