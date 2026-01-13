import hashlib
import uuid
from datetime import timedelta
from django.utils import timezone

# Clé secrète (à déplacer plus tard dans settings.py)
SECRET_KEY_RECHARGE = "SMART_WOYOFAL_SECRET"


def generate_reference():
    """
    Génère une référence unique de transaction
    """
    return str(uuid.uuid4())


def generate_recharge_token(meter_id, amount_kwh):
    """
    Génère un token sécurisé pour la recharge
    """
    raw_data = f"{meter_id}-{amount_kwh}-{uuid.uuid4()}-{SECRET_KEY_RECHARGE}"
    token = hashlib.sha256(raw_data.encode()).hexdigest()

    expires_at = timezone.now() + timedelta(minutes=10)

    return {
        "token": token,
        "expires_at": expires_at
    }
import qrcode
import base64
from io import BytesIO


def generate_qr_code(data):
    """
    Génère un QR Code encodé en Base64
    (utilisable via API REST)
    """
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return qr_base64
