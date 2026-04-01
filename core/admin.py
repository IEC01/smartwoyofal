from django.contrib import admin
from .models import User, SmartMeter, Consumption, CreditTransaction, Alert, RechargeToken, PaymentOrder


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('order_ref', 'meter', 'provider', 'amount_fcfa', 'amount_kwh', 'status', 'token_used', 'created_at')
    list_filter = ('status', 'provider', 'token_used')
    search_fields = ('order_ref', 'meter__meter_id', 'phone_number')
    readonly_fields = ('order_ref', 'token', 'token_expires_at', 'created_at', 'paid_at')


@admin.register(SmartMeter)
class SmartMeterAdmin(admin.ModelAdmin):
    list_display = ('meter_id', 'owner', 'location', 'credit_kwh', 'is_active', 'last_sync')
    list_filter = ('is_active',)
    search_fields = ('meter_id', 'owner__username')


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'meter', 'transaction_type', 'amount_kwh', 'amount_fcfa', 'is_verified', 'created_at')
    list_filter = ('transaction_type', 'is_verified')


admin.site.register(User)
admin.site.register(Consumption)
admin.site.register(Alert)
admin.site.register(RechargeToken)
