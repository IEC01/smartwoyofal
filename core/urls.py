from django.urls import path
from .views import (
    home,
    recharge_page,
    recharge_meter,
    create_payment_order,
    validate_token,
    meter_balance,
    meter_transactions,
    get_offers,
)

urlpatterns = [
    # Pages HTML
    path('', home, name='home'),
    path('recharge/', recharge_page, name='recharge'),

    # API paiement en ligne
    path('api/offers/', get_offers, name='get_offers'),
    path('api/payment/create/', create_payment_order, name='create_payment_order'),
    path('api/payment/validate/', validate_token, name='validate_token'),

    # API compteur
    path('api/meter/<str:meter_id>/balance/', meter_balance, name='meter_balance'),
    path('api/meter/<str:meter_id>/transactions/', meter_transactions, name='meter_transactions'),

    # Ancienne route (compatibilité)
    path('api/recharge/', recharge_meter, name='recharge_meter'),
]
