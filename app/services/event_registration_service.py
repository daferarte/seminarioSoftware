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
import asyncio

from app.models.event_registration import EventRegistration
from app.schemas.registration_schema import EventRegistrationCreate
from app.repositories.registration_repository import EventRegistrationRepository
from app.core.mail_config import FastMail, MessageSchema, conf


class EventRegistrationService:
    def __init__(self):
        self.repo = EventRegistrationRepository()

    # =========================
    # CRUD PRINCIPAL
    # =========================
    def create_registration(self, db: Session, data: EventRegistrationCreate):
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
        return self.repo.get_all(db)

    def get_registration(self, db: Session, reg_id: int):
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
        return reg

    def mark_as_paid(self, db: Session, reg_id: int):
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
        reg.is_paid = True
        db.commit()
        db.refresh(reg)
        return reg

    def mark_as_unpaid(self, db: Session, reg_id: int):
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
        try:
            df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al leer Excel: {str(e)}")

        required_columns = {"event_id", "participant_document_id", "registered_by_staff_id", "qr_code_sent", "is_paid"}
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(status_code=400, detail=f"Faltan columnas: {', '.join(required_columns)}")

        def parse_bool(v):
            if isinstance(v, bool): return v
            if isinstance(v, (int, float)): return v != 0
            if isinstance(v, str): return v.strip().lower() in ["true", "1", "yes", "si", "sí"]
            return False

        inserted, skipped = 0, 0
        for _, row in df.iterrows():
            try:
                event_id = int(row["event_id"])
                participant_id = str(row["participant_document_id"])
                staff_id = int(row["registered_by_staff_id"])
                qr_sent = parse_bool(row["qr_code_sent"])
                is_paid = parse_bool(row["is_paid"])
            except Exception:
                skipped += 1
                continue

            if self.repo.get_existing_registration(db, event_id=event_id, participant_document_id=participant_id):
                skipped += 1
                continue

            reg = EventRegistration(
                event_id=event_id,
                participant_document_id=participant_id,
                registered_by_staff_id=staff_id,
                qr_code_sent=qr_sent,
                qr_sent_at=datetime.utcnow() if qr_sent else None,
                is_paid=is_paid,
            )
            db.add(reg)
            inserted += 1
        db.commit()

        return {"status": "success", "inserted": inserted, "skipped": skipped}

    # =========================
    # GENERAR QR INDIVIDUAL
    # =========================
    def generate_qr_for_registration(self, db: Session, reg_id: int):
        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        event = getattr(reg, "event", None)
        participant = getattr(reg, "participant", None)

        payload = {
            "registration_id": reg.id,
            "event_id": reg.event_id,
            "participant_document_id": reg.participant_document_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        secret_key = b"ucc-seminario-secret-key"
        payload["signature"] = hmac.new(secret_key, json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()

        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(json.dumps(payload))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        event_name = (event.name if event else f"evento_{reg.event_id}").replace(" ", "_")
        save_dir = os.path.join("app", "static", "qrs", event_name)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{reg.participant_document_id}.png")
        img.save(file_path)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        base64_png = base64.b64encode(buf.getvalue()).decode()
        buf.close()

        return {
            "status": "success",
            "qr_image_path": file_path,
            "qr_image_base64": f"data:image/png;base64,{base64_png}",
        }

    # =========================
    # GENERAR Y ENVIAR QRS PAGADOS (ASÍNCRONO)
    # =========================
    async def generate_and_send_all_qrs_paid(self, db: Session, event_id: int):
        from app.models.participant import Participant
        from app.models.event import Event

        event = db.query(Event).filter_by(id=event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        regs = (
            db.query(EventRegistration)
            .filter(EventRegistration.event_id == event_id, EventRegistration.is_paid == True)
            .all()
        )
        if not regs:
            return {"message": f"No hay inscripciones pagadas para el evento '{event.name}'."}

        event_dir = os.path.join("app", "static", "qrs", event.name.replace(" ", "_"))
        os.makedirs(event_dir, exist_ok=True)

        secret_key = b"ucc-seminario-secret-key"
        fm = FastMail(conf)

        async def send_email_task(reg, participant):
            payload = {
                "registration_id": reg.id,
                "event_id": event.id,
                "participant_document_id": participant.document_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
            payload["signature"] = hmac.new(secret_key, json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()

            qr_img = qrcode.make(json.dumps(payload))
            qr_path = os.path.join(event_dir, f"{participant.document_id}.png")
            qr_img.save(qr_path)

            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            qr_base64 = base64.b64encode(buf.getvalue()).decode()
            buf.close()
            qr_inline = f"data:image/png;base64,{qr_base64}"

            verify_url = f"https://iemchambu2.edu.co/verify-qr/{reg.id}"

            html_body = f"""
            <div style="font-family: Arial, sans-serif; color: #222; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #004b87;">Plantilla para Entrega de QR de Acceso a Seminario de Ingeniería</h2>
                <p>¡Hola, <b>{participant.first_name} {participant.last_name}</b>!</p>

                <p>Tu acceso para el seminario de ingeniería <b>{event.name}</b> programado para <b>viernes, 17 de octubre de 2025</b>, está listo.</p>

                <p>A continuación encontrarás tu código QR personal e intransferible. Por favor, preséntalo en la entrada para agilizar tu registro:</p>

                <div style="text-align:center; margin:20px 0;">
                    <img src="{qr_inline}" alt="Código QR" style="width:200px; height:200px; border:2px solid #004b87; padding:5px; border-radius:8px;">
                </div>

                <p>También puedes verificar tu registro haciendo clic en el siguiente enlace:</p>
                <p style="text-align:center; margin: 20px 0;">
                    <a href="{verify_url}" style="background-color:#004b87; color:#fff; text-decoration:none; padding:10px 20px; border-radius:5px;">Verificar mi QR</a>
                </p>

                <p>¡Te esperamos! 👋</p>

                <hr style="border:none; border-top:1px solid #ddd;">
                <p style="font-size:12px; color:#666; text-align:center;">
                    Universidad Cooperativa de Colombia - Campus Pasto<br>
                    Seminario de Ingeniería de Software<br>
                    © 2025 Todos los derechos reservados.
                </p>
            </div>
            """

            message = MessageSchema(
                subject=f"Tu Acceso al {event.name}",
                recipients=[participant.email],
                body=html_body,
                subtype="html",
                attachments=[qr_path],
            )

            await fm.send_message(message)
            return participant.email

        tasks = []
        for reg in regs:
            participant = db.query(Participant).filter_by(document_id=reg.participant_document_id).first()
            if participant and participant.email:
                tasks.append(send_email_task(reg, participant))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        sent = [r for r in results if isinstance(r, str)]
        failed = [str(r) for r in results if isinstance(r, Exception)]

        return {
            "status": "success",
            "event": event.name,
            "generated_qrs": len(regs),
            "emails_sent": len(sent),
            "failed_emails": failed,
            "message": f"✅ {len(sent)} correos enviados correctamente para el evento '{event.name}'."
        }

    # =========================
    # ENVIAR UN SOLO QR POR CORREO (PRUEBA)
    # =========================
    async def send_single_qr(self, db: Session, reg_id: int):
        from app.models.participant import Participant
        from app.models.event import Event

        reg = self.repo.get_by_id(db, reg_id)
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        participant = db.query(Participant).filter_by(document_id=reg.participant_document_id).first()
        event = db.query(Event).filter_by(id=reg.event_id).first()

        if not participant or not participant.email:
            raise HTTPException(status_code=404, detail="Participant not found or email missing")

        secret_key = b"ucc-seminario-secret-key"
        payload = {
            "registration_id": reg.id,
            "event_id": reg.event_id,
            "participant_document_id": participant.document_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        payload["signature"] = hmac.new(secret_key, json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()

        qr_img = qrcode.make(json.dumps(payload))
        event_dir = os.path.join("app", "static", "qrs", event.name.replace(" ", "_"))
        os.makedirs(event_dir, exist_ok=True)
        qr_path = os.path.join(event_dir, f"{participant.document_id}.png")
        qr_img.save(qr_path)

        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        qr_inline = f"data:image/png;base64,{qr_base64}"

        verify_url = f"https://iemchambu2.edu.co/verify-qr/{reg.id}"

        html_body = f"""
        <div style="font-family: Arial, sans-serif; color: #222; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #004b87;">Plantilla para Entrega de QR de Acceso a Seminario de Ingeniería</h2>
            <p>¡Hola, <b>{participant.first_name} {participant.last_name}</b>!</p>

            <p>Tu acceso para el seminario de ingeniería <b>{event.name}</b> programado para <b>viernes, 17 de octubre de 2025</b>, está listo.</p>

            <p>A continuación encontrarás tu código QR personal e intransferible. Por favor, preséntalo en la entrada para agilizar tu registro:</p>

            <div style="text-align:center; margin:20px 0;">
                <img src="{qr_inline}" alt="Código QR" style="width:200px; height:200px; border:2px solid #004b87; padding:5px; border-radius:8px;">
            </div>

            <p>También puedes verificar tu registro haciendo clic en el siguiente enlace:</p>
            <p style="text-align:center; margin: 20px 0;">
                <a href="{verify_url}" style="background-color:#004b87; color:#fff; text-decoration:none; padding:10px 20px; border-radius:5px;">Verificar mi QR</a>
            </p>

            <p>¡Te esperamos! 👋</p>

            <hr style="border:none; border-top:1px solid #ddd;">
            <p style="font-size:12px; color:#666; text-align:center;">
                Universidad Cooperativa de Colombia - Campus Pasto<br>
                Seminario de Ingeniería de Software<br>
                © 2025 Todos los derechos reservados.
            </p>
        </div>
        """

        fm = FastMail(conf)
        message = MessageSchema(
            subject=f"Tu Acceso al {event.name}",
            recipients=[participant.email],
            body=html_body,
            subtype="html",
            attachments=[qr_path],
        )

        await fm.send_message(message)

        reg.qr_code_sent = True
        reg.qr_sent_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "message": f"Correo enviado correctamente a {participant.email}",
            "participant": f"{participant.first_name} {participant.last_name}",
            "event": event.name,
            "email": participant.email,
            "qr_image": f"data:image/png;base64,{qr_base64}"
        }
