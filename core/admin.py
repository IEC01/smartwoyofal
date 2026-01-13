from django.contrib import admin
from django.contrib import admin
from .models import User, SmartMeter, Consumption, CreditTransaction, Alert

admin.site.register(User)
admin.site.register(SmartMeter)
admin.site.register(Consumption)
admin.site.register(CreditTransaction)
admin.site.register(Alert)


# Register your models here.
