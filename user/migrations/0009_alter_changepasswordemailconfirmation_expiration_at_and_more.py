# Generated by Django 5.0.4 on 2024-07-12 11:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_alter_changepasswordemailconfirmation_expiration_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changepasswordemailconfirmation',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 11, 32, 56, 359107, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='emailcode',
            name='expiration_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 12, 11, 32, 56, 358694, tzinfo=datetime.timezone.utc)),
        ),
    ]
