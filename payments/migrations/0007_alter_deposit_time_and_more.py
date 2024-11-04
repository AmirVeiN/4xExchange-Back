# Generated by Django 5.0.4 on 2024-07-12 09:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_alter_deposit_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 9, 16, 1, 67467, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='depositrequest',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 10, 16, 1, 67796, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='withdrawemailconfirmation',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 9, 21, 1, 68056, tzinfo=datetime.timezone.utc)),
        ),
    ]