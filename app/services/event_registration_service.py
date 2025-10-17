import qrcode
import io
import base64
from fastapi import HTTPException 
from app.core.qr_utils import sign_qr_payload
from app.models.event_registration import EventRegistration
from app.models.event import Event

class EventRegistrationService:
    # ... tus métodos anteriores ...

    def generate_qr_for_registration(self, db: Session, registration_id: int):
        """Genera un QR firmado en formato PNG para el registro especificado."""
        reg = db.query(EventRegistration).filter_by(id=registration_id).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        event = db.query(Event).filter_by(id=reg.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        payload = {
            "registration_id": reg.id,
            "participant_document_id": reg.participant_document_id,
            "event_id": reg.event_id,
            "event_name": event.name,
            "timestamp": datetime.utcnow().isoformat(),
        }

        signed_payload = sign_qr_payload(payload)

        # Generar QR en memoria
        qr_img = qrcode.make(signed_payload)
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "registration_id": reg.id,
            "event": event.name,
            "participant": reg.participant_document_id,
            "qr_image_base64": f"data:image/png;base64,{qr_base64}",
        }
