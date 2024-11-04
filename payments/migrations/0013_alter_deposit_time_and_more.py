# Generated by Django 5.0.4 on 2024-07-12 12:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_alter_deposit_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 12, 37, 56, 764423, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='depositrequest',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 13, 37, 56, 764828, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='withdrawemailconfirmation',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 12, 42, 56, 765263, tzinfo=datetime.timezone.utc)),
        ),
    ]
