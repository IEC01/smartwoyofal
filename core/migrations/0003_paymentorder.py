from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rechargetoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_ref', models.CharField(max_length=100, unique=True)),
                ('amount_fcfa', models.IntegerField()),
                ('amount_kwh', models.FloatField()),
                ('provider', models.CharField(
                    choices=[('wave', 'Wave'), ('orange_money', 'Orange Money'), ('free_money', 'Free Money')],
                    max_length=20
                )),
                ('phone_number', models.CharField(max_length=20)),
                ('status', models.CharField(
                    choices=[('pending', 'En attente'), ('paid', 'Payé'), ('failed', 'Échoué'), ('expired', 'Expiré')],
                    default='pending',
                    max_length=20
                )),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
                ('token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('token_used', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('meter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.smartmeter')),
            ],
        ),
    ]
