from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import SmartMeter, PaymentOrder, CreditTransaction
from .serializers import CreatePaymentOrderSerializer, ValidateTokenSerializer
from .utils import (
    generate_order_ref,
    generate_recharge_token,
    generate_reference,
    generate_qr_code,
    simulate_mobile_payment,
    CREDIT_OFFERS,
    fcfa_to_kwh,
)


# ─────────────────────────────────────────────
# PAGES HTML
# ─────────────────────────────────────────────

def home(request):
    return render(request, 'core/home.html')


def recharge_page(request):
    return render(request, 'core/recharge.html', {'offers': CREDIT_OFFERS})


# ─────────────────────────────────────────────
# API : OFFRES
# ─────────────────────────────────────────────

@api_view(['GET'])
def get_offers(request):
    return Response({"offers": CREDIT_OFFERS})


# ─────────────────────────────────────────────
# API : SOLDE DU COMPTEUR
# ─────────────────────────────────────────────

@api_view(['GET'])
def meter_balance(request, meter_id):
    try:
        meter = SmartMeter.objects.get(meter_id=meter_id, is_active=True)
    except SmartMeter.DoesNotExist:
        return Response({"error": "Compteur introuvable ou inactif."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "meter_id":   meter.meter_id,
        "credit_kwh": round(meter.credit_kwh, 2),
        "location":   meter.location,
        "is_active":  meter.is_active,
    })


# ─────────────────────────────────────────────
# API : HISTORIQUE
# ─────────────────────────────────────────────

@api_view(['GET'])
def meter_transactions(request, meter_id):
    try:
        meter = SmartMeter.objects.get(meter_id=meter_id)
    except SmartMeter.DoesNotExist:
        return Response({"error": "Compteur introuvable."}, status=status.HTTP_404_NOT_FOUND)

    transactions = CreditTransaction.objects.filter(
        meter=meter, transaction_type='recharge'
    ).order_by('-created_at')[:20]

    data = [{
        "reference":  t.reference,
        "amount_kwh": t.amount_kwh,
        "amount_fcfa": t.amount_fcfa,
        "date": t.created_at.strftime('%d/%m/%Y %H:%M'),
    } for t in transactions]

    return Response({"meter_id": meter_id, "transactions": data})


# ─────────────────────────────────────────────
# API : CRÉER UNE COMMANDE DE PAIEMENT
# ─────────────────────────────────────────────

@csrf_exempt
@api_view(['POST'])
def create_payment_order(request):
    """
    Étape 1 : Crée la commande, simule le paiement mobile, génère le token.
    """
    serializer = CreatePaymentOrderSerializer(data=request.data)
    if not serializer.is_valid():
        # Retourner les erreurs de validation clairement
        return Response(
            {"success": False, "error": "Données invalides.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    data        = serializer.validated_data
    amount_fcfa = data['amount_fcfa']
    amount_kwh  = fcfa_to_kwh(amount_fcfa)
    provider    = data['provider']
    phone       = data['phone_number']

    try:
        meter = SmartMeter.objects.get(meter_id=data['meter_id'], is_active=True)
    except SmartMeter.DoesNotExist:
        return Response(
            {"success": False, "error": "Compteur introuvable ou inactif."},
            status=status.HTTP_404_NOT_FOUND
        )

    order_ref = generate_order_ref()
    order = PaymentOrder.objects.create(
        meter=meter,
        order_ref=order_ref,
        amount_fcfa=amount_fcfa,
        amount_kwh=amount_kwh,
        provider=provider,
        phone_number=phone,
        status='pending',
    )

    # Simulation du paiement mobile
    payment_result = simulate_mobile_payment(provider, phone, amount_fcfa, order_ref)

    if not payment_result['success']:
        order.status = 'failed'
        order.save()
        return Response({
            "success": False,
            "order_ref": order_ref,
            "message": payment_result['message'],
        }, status=status.HTTP_402_PAYMENT_REQUIRED)

    # Paiement confirmé → token
    token_data = generate_recharge_token(meter.meter_id, amount_kwh)
    order.status          = 'paid'
    order.token           = token_data['token']
    order.token_expires_at = token_data['expires_at']
    order.paid_at         = timezone.now()
    order.save()

    qr_code = generate_qr_code(token_data['token'])

    return Response({
        "success":          True,
        "order_ref":        order_ref,
        "transaction_id":   payment_result['transaction_id'],
        "message":          payment_result['message'],
        "meter_id":         meter.meter_id,
        "amount_fcfa":      amount_fcfa,
        "amount_kwh":       amount_kwh,
        "token":            token_data['token'],
        "token_expires_at": token_data['expires_at'],
        "qr_code":          qr_code,
    }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# API : VALIDER LE TOKEN
# ─────────────────────────────────────────────

@csrf_exempt
@api_view(['POST'])
def validate_token(request):
    """
    Étape 2 : Valide le token et crédite le compteur.
    """
    serializer = ValidateTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"success": False, "error": "Données invalides.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    meter_id    = serializer.validated_data['meter_id']
    token_value = serializer.validated_data['token']

    try:
        meter = SmartMeter.objects.get(meter_id=meter_id, is_active=True)
    except SmartMeter.DoesNotExist:
        return Response({"success": False, "error": "Compteur introuvable ou inactif."}, status=status.HTTP_404_NOT_FOUND)

    try:
        order = PaymentOrder.objects.get(
            token=token_value,
            meter=meter,
            status='paid',
            token_used=False,
        )
    except PaymentOrder.DoesNotExist:
        return Response({"success": False, "error": "Token invalide ou déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now() > order.token_expires_at:
        order.status = 'expired'
        order.save()
        return Response({"success": False, "error": "Token expiré. Effectuez un nouveau paiement."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Créditer le compteur
    meter.credit_kwh += order.amount_kwh
    meter.save()

    order.token_used = True
    order.save()

    CreditTransaction.objects.create(
        meter=meter,
        amount_kwh=order.amount_kwh,
        amount_fcfa=order.amount_fcfa,
        transaction_type='recharge',
        reference=generate_reference(),
        is_verified=True,
    )

    return Response({
        "success":         True,
        "message":         f"{order.amount_kwh} kWh ajoutés avec succès.",
        "meter_id":        meter.meter_id,
        "credited_kwh":    order.amount_kwh,
        "new_balance_kwh": round(meter.credit_kwh, 2),
        "amount_fcfa":     order.amount_fcfa,
    }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# ANCIENNE VUE (compatibilité)
# ─────────────────────────────────────────────

@api_view(['POST'])
def recharge_meter(request):
    meter_id   = request.data.get('meter_id')
    amount_kwh = request.data.get('amount_kwh')

    if not meter_id or not amount_kwh:
        return Response({"error": "meter_id et amount_kwh sont requis"}, status=status.HTTP_400_BAD_REQUEST)

    reference  = generate_reference()
    token_data = generate_recharge_token(meter_id, amount_kwh)
    qr_code    = generate_qr_code(token_data["token"])

    return Response({
        "reference":  reference,
        "meter_id":   meter_id,
        "amount_kwh": amount_kwh,
        "token":      token_data["token"],
        "expires_at": token_data["expires_at"],
        "qr_code":    qr_code,
    }, status=status.HTTP_201_CREATED)
