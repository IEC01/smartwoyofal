from django.urls import path
from .views import recharge_meter

urlpatterns = [
    path('recharge/', recharge_meter),
]

from .views import recharge_meter, home

urlpatterns = [
    path('', home),
    path('recharge/', recharge_meter),
]
