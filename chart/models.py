from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ChartPrice(models.Model):
    name = models.CharField(default="token", max_length=10)
    number = models.FloatField(default=0)

    def __str__(self):
        return str(self.name)


class NumberChange(models.Model):
    my_model = models.ForeignKey(ChartPrice, on_delete=models.CASCADE)
    value = models.FloatField()
    time = models.DateTimeField(default=timezone.now)
    open = models.FloatField(null=True, blank=True, db_column='open_value')
    high = models.FloatField(null=True, blank=True, db_column='high_value')
    low = models.FloatField(null=True, blank=True, db_column='low_value')
    close = models.FloatField(null=True, blank=True, db_column='close_value')

    @classmethod
    def create(cls, my_model, new_number):
        number_change = cls(my_model=my_model, value=new_number)
        number_change.save()

    def __str__(self):
        return str(self.value)


@receiver(post_save, sender=NumberChange)
def send_update_to_websocket(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        data = {
            "time": int(
                instance.time.timestamp()
            ),  # Assuming instance.time is aware datetime
            "open": instance.open,
            "high": instance.high,
            "low": instance.low,
            "close": instance.close,
        }

        async_to_sync(channel_layer.group_send)(
            "chart_data_group", {"type": "send_chart_data", "message": json.dumps(data)}
        )


class ScheduledNumberChange(models.Model):
    my_model = models.ForeignKey(ChartPrice, on_delete=models.CASCADE)
    number = models.FloatField()
    run_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1, period=IntervalSchedule.SECONDS
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name=f"Change number for {self.my_model.id} at {self.run_at}",
            task="chart.tasks.change_number",
            args=json.dumps([self.my_model.id, self.number]),
            one_off=True,
            start_time=self.run_at,
        )

    def __str__(self):
        return f"{self.number} at {self.run_at}"


class ChangeVolume24(models.Model):
    name = models.CharField(default="volume", max_length=10)
    number = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return str(self.name)


@receiver(post_save, sender=ChangeVolume24)
def send_volume_update_to_websocket(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    volume_data = {
        "volume_24h": ChangeVolume24.objects.get(name="volume").number,
    }

    async_to_sync(channel_layer.group_send)(
        "chart_data_group",
        {"type": "send_volume_data", "message": json.dumps(volume_data)},
    )
