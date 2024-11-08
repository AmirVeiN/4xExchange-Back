# Generated by Django 5.0.4 on 2024-07-12 08:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_alter_deposit_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 8, 45, 47, 491101, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='depositrequest',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 9, 45, 47, 491503, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='withdrawemailconfirmation',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 8, 50, 47, 491890, tzinfo=datetime.timezone.utc)),
        ),
    ]
