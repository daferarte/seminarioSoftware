import hmac
import hashlib
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "clave_fallback_segura")

def sign_qr_payload(data: dict) -> str:
    """Crea un payload firmado y codificado en base64"""
    json_data = json.dumps(data, separators=(",", ":"))
    signature = hmac.new(
        SECRET_KEY.encode(),
        msg=json_data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    data["signature"] = signature
    encoded = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return encoded

def verify_qr_signature(data: dict) -> bool:
    """Verifica que la firma del QR sea válida"""
    if "signature" not in data:
        return False
    signature = data["signature"]
    data_copy = {k: v for k, v in data.items() if k != "signature"}
    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        msg=json.dumps(data_copy, separators=(",", ":")).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
