from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
import hmac, hashlib, json

from app.models.attendance import Attendance
from app.models.event_registration import EventRegistration


class AttendanceService:
    def __init__(self):
        self.secret_key = b"ucc-seminario-secret-key"

    def _validate_qr_signature(self, payload: dict):
        """
        Verifica la firma HMAC del QR para asegurar integridad y autenticidad.
        """
        data = payload.copy()
        signature = data.pop("signature", None)
        if not signature:
            raise HTTPException(status_code=400, detail="QR sin firma")

        computed_sig = hmac.new(
            self.secret_key,
            json.dumps(data, sort_keys=True).encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, computed_sig):
            raise HTTPException(status_code=400, detail="QR no válido o manipulado")

        return data

    def check_in_or_out(self, db: Session, qr_payload: dict):
        """
        Recibe el JSON del QR, valida la firma y registra check-in o check-out automáticamente.
        """
        # ✅ Validar firma e integridad
        payload = self._validate_qr_signature(qr_payload)

        registration_id = payload.get("registration_id")
        if not registration_id:
            raise HTTPException(status_code=400, detail="Falta registration_id en el QR")

        # Buscar registro de inscripción
        reg = db.query(EventRegistration).filter_by(id=registration_id).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Event registration not found")

        # Buscar asistencia previa
        attendance = (
            db.query(Attendance)
            .filter(Attendance.registration_id == registration_id)
            .order_by(Attendance.id.desc())
            .first()
        )

        now = datetime.utcnow()

        # 🟢 No existe asistencia previa → registrar entrada
        if not attendance or attendance.status == "CHECKED_OUT":
            new_attendance = Attendance(
                registration_id=registration_id,
                participant_document_id=reg.participant_document_id,
                event_id=reg.event_id,
                check_in_time=now,
                status="CHECKED_IN",
            )
            db.add(new_attendance)
            db.commit()
            db.refresh(new_attendance)
            return {
                "message": f"✅ Check-in registrado para {reg.participant_document_id}",
                "data": {
                    "id": new_attendance.id,
                    "status": new_attendance.status,
                    "check_in_time": new_attendance.check_in_time.isoformat(),
                },
            }

        # 🔴 Ya tenía entrada activa → registrar salida
        elif attendance.status == "CHECKED_IN" and not attendance.check_out_time:
            attendance.check_out_time = now
            attendance.status = "CHECKED_OUT"
            db.commit()
            db.refresh(attendance)
            return {
                "message": f"👋 Check-out registrado para {reg.participant_document_id}",
                "data": {
                    "id": attendance.id,
                    "status": attendance.status,
                    "check_out_time": attendance.check_out_time.isoformat(),
                },
            }

        # 🚫 Caso inválido (ya completó entrada/salida)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asistencia ya completada o inválida."
            )
