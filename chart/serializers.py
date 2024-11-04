from rest_framework import serializers
from .models import ChangeVolume24, NumberChange, ScheduledNumberChange, ChartPrice


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChartPrice
        fields = ["number"]


class VolumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChangeVolume24
        fields = ["number"]


class ChartDataSerializers(serializers.ModelSerializer):

    class Meta:
        model = NumberChange
        fields = ["value", "time"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class ChartDetailSerializers(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()

    class Meta:
        model = ChartPrice
        fields = ["price", "volume"]

    def get_price(self, obj):
        price = ChartPrice.objects.get(name="token")
        return PriceSerializer(price).data

    def get_volume(self, obj):
        volume = ChangeVolume24.objects.get(name="volume")
        return VolumeSerializer(volume).data


class TemporaryChartDataSerializer(serializers.ModelSerializer):

    run_at = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledNumberChange
        fields = ["number", "run_at"]

    def get_run_at(self, obj):
        return obj.run_at.strftime("%Y-%m-%d %H:%M")


class ChartChangePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScheduledNumberChange
        fields = ["number", "run_at"]
