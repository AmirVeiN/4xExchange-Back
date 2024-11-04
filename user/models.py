from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from user.managers import UserManager
from . import constants as user_constants
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
import json


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    username = models.CharField(unique=True, max_length=255, db_index=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    user_type = models.PositiveSmallIntegerField(
        choices=user_constants.USER_TYPE_CHOICES
    )

    usdt = models.FloatField(default=0)
    token = models.FloatField(default=0)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    objects = UserManager()


class EmailCode(models.Model):
    email = models.EmailField()
    code = models.IntegerField()
    run_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        delete_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5, period=IntervalSchedule.MINUTES
        )
        PeriodicTask.objects.create(
            interval=delete_schedule,
            name=f"Delete_UserEmailCode_{self.code}_at_{self.expiration_at} ",
            task="user.tasks.delete_email_code_verification",
            args=json.dumps([self.pk, self.code]),
            one_off=True,
            start_time=timezone.now() + timedelta(minutes=5),
        )


class ChangePasswordEmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()
    run_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        delete_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5, period=IntervalSchedule.MINUTES
        )
        PeriodicTask.objects.create(
            interval=delete_schedule,
            name=f"Delete_PasswordEmailCode_{self.code}_at_{self.expiration_at} ",
            task="user.tasks.delete_email_code",
            args=json.dumps([self.pk, self.code]),
            one_off=True,
            start_time=timezone.now() + timedelta(minutes=5),
        )
