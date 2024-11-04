# Generated by Django 5.0.4 on 2024-05-14 12:27

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tether', models.FloatField()),
                ('tokenRecive', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('tokenPrice', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userBuyToken', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tether', models.CharField(max_length=100)),
                ('actually_tether', models.CharField(max_length=500)),
                ('wallet', models.CharField(max_length=500)),
                ('time', models.DateTimeField(default=datetime.datetime(2024, 5, 14, 12, 27, 58, 227555, tzinfo=datetime.timezone.utc))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledDepositCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tether', models.CharField(max_length=100)),
                ('wallet', models.CharField(max_length=500)),
                ('actually_tether', models.CharField(max_length=500)),
                ('run_at', models.DateTimeField(auto_now_add=True)),
                ('expiration_at', models.DateTimeField(default=datetime.datetime(2024, 5, 14, 13, 27, 58, 227848, tzinfo=datetime.timezone.utc))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SellToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tetherRecive', models.FloatField()),
                ('token', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('tokenPrice', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userSellToken', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawEmailConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('withdraw', models.FloatField()),
                ('wallet', models.CharField(max_length=500)),
                ('run_at', models.DateTimeField(auto_now_add=True)),
                ('expiration_at', models.DateTimeField(default=datetime.datetime(2024, 5, 14, 12, 32, 58, 228100, tzinfo=datetime.timezone.utc))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tether', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Accept'), (3, 'Reject')])),
                ('wallet', models.CharField(max_length=500)),
                ('text', models.CharField(blank=True, max_length=30, null=True)),
                ('answer', models.DateTimeField(blank=True, null=True)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='admin', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
