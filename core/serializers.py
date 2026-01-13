from rest_framework import serializers
from .models import SmartMeter, CreditTransaction

class RechargeSerializer(serializers.Serializer):
    meter_id = serializers.CharField()
    token = serializers.CharField()
