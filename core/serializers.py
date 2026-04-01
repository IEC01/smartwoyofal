from rest_framework import serializers
from .models import SmartMeter, PaymentOrder
from .utils import TARIF_KWH, fcfa_to_kwh


class CreatePaymentOrderSerializer(serializers.Serializer):
    meter_id = serializers.CharField()
    amount_fcfa = serializers.IntegerField(min_value=500)
    provider = serializers.ChoiceField(choices=['wave', 'orange_money', 'free_money'])
    phone_number = serializers.CharField(max_length=20)

    def validate_amount_fcfa(self, value):
        if value % 500 != 0:
            raise serializers.ValidationError("Le montant doit être un multiple de 500 FCFA.")
        return value

    def validate_meter_id(self, value):
        if not SmartMeter.objects.filter(meter_id=value, is_active=True).exists():
            raise serializers.ValidationError("Compteur introuvable ou inactif.")
        return value


class ValidateTokenSerializer(serializers.Serializer):
    meter_id = serializers.CharField()
    token = serializers.CharField()


class RechargeSerializer(serializers.Serializer):
    meter_id = serializers.CharField()
    token = serializers.CharField()
