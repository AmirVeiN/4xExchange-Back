from datetime import timedelta
from django.db import models
from user.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
import json
from .choices import USER_TYPE_CHOICES


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tether = models.CharField(max_length=100)
    wallet = models.CharField(max_length=500)
    crypto_type = models.CharField(max_length=100, default="USDT (BEP20)")
    time = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.user} - {self.tether}"


class DepositRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tether = models.CharField(max_length=100)
    wallet = models.CharField(max_length=500)
    crypto_type = models.CharField(max_length=100, default="USDT (BEP20)")
    run_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=60))

    def __str__(self):
        return f"{self.user} - {self.tether}"


# class ScheduledDepositCheck(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     tether = models.CharField(max_length=100)
#     wallet = models.CharField(max_length=500)
#     actually_tether = models.CharField(max_length=500)
#     run_at = models.DateTimeField(auto_now_add=True)
#     expiration_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=60))

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         schedule, created = IntervalSchedule.objects.get_or_create(
#             every=5, period=IntervalSchedule.MINUTES
#         )
#         PeriodicTask.objects.create(
#             interval=schedule,
#             name=f"Check Tether {self.tether} at {self.run_at}",
#             task="payments.tasks.check_deposit",
#             args=json.dumps(
#                 [self.tether, self.user.pk, self.pk, self.wallet, self.actually_tether]
#             ),
#             one_off=False,
#             start_time=self.run_at,
#         )

#         delete_schedule, _ = IntervalSchedule.objects.get_or_create(
#             every=60, period=IntervalSchedule.MINUTES
#         )
#         PeriodicTask.objects.create(
#             interval=delete_schedule,
#             name=f"Delete Check Task {self.pk} at {self.expiration_at}",
#             task="payments.tasks.delete_task",
#             args=json.dumps([self.pk, self.tether]),
#             one_off=True,
#             start_time=timezone.now() + timedelta(minutes=60),
#         )


class WithdrawEmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()
    withdraw = models.FloatField()
    wallet = models.CharField(max_length=500)
    run_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        delete_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5, period=IntervalSchedule.MINUTES
        )
        PeriodicTask.objects.create(
            interval=delete_schedule,
            name=f"Delete_EmailCode_{self.code}_at_{self.expiration_at} ",
            task="payments.tasks.delete_email_code",
            args=json.dumps([self.pk, self.code]),
            one_off=True,
            start_time=timezone.now() + timedelta(minutes=5),
        )


class WithdrawRequest(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    tether = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    wallet = models.CharField(max_length=500)
    text = models.CharField(max_length=30, null=True, blank=True)
    admin = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="admin"
    )
    answer = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.tether} - {self.status}"


class BuyToken(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userBuyToken"
    )
    tether = models.FloatField()
    tokenRecive = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    tokenPrice = models.FloatField()

    def __str__(self):
        return f"{self.user} - {self.tether} - {self.tokenRecive}"


class SellToken(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userSellToken"
    )
    tetherRecive = models.FloatField()
    token = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    tokenPrice = models.FloatField()

    def __str__(self):
        return f"{self.user} - {self.tetherRecive} - {self.token}"
