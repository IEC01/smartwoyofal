from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('technicien', 'Technicien'),
        ('admin', 'Administrateur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)


class SmartMeter(models.Model):
    meter_id = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    credit_kwh = models.FloatField(default=0.0)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.meter_id


class Consumption(models.Model):
    meter = models.ForeignKey(SmartMeter, on_delete=models.CASCADE)
    voltage = models.FloatField()
    current = models.FloatField()
    power = models.FloatField()
    energy = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class CreditTransaction(models.Model):
    meter = models.ForeignKey(SmartMeter, on_delete=models.CASCADE)
    amount_kwh = models.FloatField()
    amount_fcfa = models.IntegerField()
    TRANSACTION_TYPE = (
        ('recharge', 'Recharge'),
        ('debit', 'Debit'),
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    reference = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    ALERT_TYPE = (
        ('low_credit', 'Crédit faible'),
        ('fraud', 'Fraude'),
        ('offline', 'Hors ligne'),
    )
    meter = models.ForeignKey(SmartMeter, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE)
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class RechargeToken(models.Model):
    meter = models.ForeignKey(SmartMeter, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    amount_kwh = models.FloatField()
    amount_fcfa = models.IntegerField()
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class PaymentOrder(models.Model):
    """
    Commande de paiement créée quand l'utilisateur veut acheter du crédit.
    Après confirmation du paiement mobile, un token est généré.
    L'utilisateur saisit ce token pour créditer son compteur.
    """
    PROVIDER_CHOICES = (
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
        ('free_money', 'Free Money'),
    )
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
        ('expired', 'Expiré'),
    )

    meter = models.ForeignKey(SmartMeter, on_delete=models.CASCADE)
    order_ref = models.CharField(max_length=100, unique=True)
    amount_fcfa = models.IntegerField()
    amount_kwh = models.FloatField()
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Token généré après paiement confirmé
    token = models.CharField(max_length=255, null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    token_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_ref} - {self.provider} - {self.status}"
