import hashlib
import uuid
from datetime import timedelta
from django.utils import timezone
import qrcode
import base64
from io import BytesIO

# Clé secrète (à déplacer dans settings.py en production)
SECRET_KEY_RECHARGE = "SMART_WOYOFAL_SECRET"

# Tarif : 1 kWh = 120 FCFA (tarif SENELEC résidentiel simplifié)
TARIF_KWH = 120

# Offres prédéfinies
CREDIT_OFFERS = [
    {"fcfa": 500,   "kwh": round(500 / TARIF_KWH, 2),  "label": "Starter"},
    {"fcfa": 1000,  "kwh": round(1000 / TARIF_KWH, 2), "label": "Basic"},
    {"fcfa": 2500,  "kwh": round(2500 / TARIF_KWH, 2), "label": "Standard"},
    {"fcfa": 5000,  "kwh": round(5000 / TARIF_KWH, 2), "label": "Premium"},
    {"fcfa": 10000, "kwh": round(10000 / TARIF_KWH, 2),"label": "Pro"},
]


def generate_reference():
    """Génère une référence unique de transaction."""
    return str(uuid.uuid4()).replace('-', '').upper()[:16]


def generate_order_ref():
    """Génère une référence unique de commande paiement."""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    rand = str(uuid.uuid4()).replace('-', '').upper()[:6]
    return f"SW-{timestamp}-{rand}"


def generate_recharge_token(meter_id, amount_kwh):
    """Génère un token sécurisé pour la recharge."""
    raw_data = f"{meter_id}-{amount_kwh}-{uuid.uuid4()}-{SECRET_KEY_RECHARGE}"
    token = hashlib.sha256(raw_data.encode()).hexdigest()
    expires_at = timezone.now() + timedelta(hours=24)
    return {"token": token, "expires_at": expires_at}


def simulate_mobile_payment(provider, phone_number, amount_fcfa, order_ref):
    """
    Simule un paiement mobile (Wave / Orange Money / Free Money).
    En production, remplacer par l'appel API réel du fournisseur.

    Retourne:
        dict avec 'success', 'transaction_id', 'message'
    """
    # Simulation : tout numéro valide est accepté sauf ceux commençant par 000
    if phone_number.startswith('000'):
        return {
            "success": False,
            "transaction_id": None,
            "message": f"Échec du paiement {provider} : numéro invalide ou solde insuffisant."
        }

    provider_names = {
        'wave': 'Wave',
        'orange_money': 'Orange Money',
        'free_money': 'Free Money',
    }

    transaction_id = f"{provider.upper()[:3]}-{uuid.uuid4().hex[:10].upper()}"

    return {
        "success": True,
        "transaction_id": transaction_id,
        "message": f"Paiement {provider_names.get(provider, provider)} de {amount_fcfa} FCFA confirmé.",
    }


def generate_qr_code(data):
    """Génère un QR Code encodé en Base64."""
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def kwh_to_fcfa(kwh):
    return int(kwh * TARIF_KWH)


def fcfa_to_kwh(fcfa):
    return round(fcfa / TARIF_KWH, 2)
