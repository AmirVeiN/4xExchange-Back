# Generated by Django 5.0.4 on 2024-05-17 18:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changepasswordemailconfirmation',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 17, 18, 18, 55, 993940, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='emailcode',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 17, 18, 18, 55, 993691, tzinfo=datetime.timezone.utc)),
        ),
    ]
