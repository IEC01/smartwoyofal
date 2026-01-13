from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import generate_reference, generate_recharge_token
from .utils import generate_reference, generate_recharge_token, generate_qr_code

@api_view(['POST'])
def recharge_meter(request):
    meter_id = request.data.get('meter_id')
    amount_kwh = request.data.get('amount_kwh')

    if not meter_id or not amount_kwh:
        return Response(
            {"error": "meter_id et amount_kwh sont requis"},
            status=status.HTTP_400_BAD_REQUEST
        )

    reference = generate_reference()
    token_data = generate_recharge_token(meter_id, amount_kwh)

    qr_code = generate_qr_code(token_data["token"])

    return Response({
        "reference": reference,
        "meter_id": meter_id,
        "amount_kwh": amount_kwh,
        "token": token_data["token"],
        "expires_at": token_data["expires_at"],
        "qr_code": qr_code
    }, status=status.HTTP_201_CREATED)

from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "API Smart Woyofal opérationnelle 🚀"
    })

