import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChangeVolume24, NumberChange
from channels.db import database_sync_to_async
from datetime import datetime, timedelta
from django.utils import timezone


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chart_data_group", self.channel_name)
        await self.accept()

        volume_data = await self.get_volume_data()
        await self.send(text_data=json.dumps(volume_data))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chart_data_group", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        keyword = text_data_json.get("keyword", "")
        request = text_data_json.get("request", "")
        page = text_data_json.get("page", 1)
        page_size = text_data_json.get("page_size", 1000)

        if request == "volume":
            volume_data = await self.get_volume_data()
            await self.send(text_data=json.dumps(volume_data))
            return
        elif request == "chart":
            if keyword in ["1Min", "5Min", "1Hour", "1Day"]:
                chart_data = await self.get_chart_data(keyword, page, page_size)
                await self.send(text_data=json.dumps(chart_data))
            elif keyword == "price":
                data = await self.get_price_data()
                await self.send(text_data=json.dumps(data))
        else:
            await self.send(text_data=json.dumps({"error": "کلمه کلیدی نامعتبر"}))

    async def send_chart_data(self, event):
        message = event["message"]
        await self.send(text_data=message)

    async def send_volume_data(self, event):
        message = event["message"]
        await self.send(text_data=message)

    @database_sync_to_async
    def get_volume_data(self):
        try:
            volume_instance = ChangeVolume24.objects.latest("id")
            return {"volume_24h": volume_instance.number}
        except ChangeVolume24.DoesNotExist:
            return {"volume_24h": 0}

    @database_sync_to_async
    def get_price_data(self):
        try:
            price = NumberChange.objects.latest("id")
            return {"close": price.close}
        except NumberChange.DoesNotExist:
            return {"price": 0}

    @database_sync_to_async
    def get_chart_data(self, keyword, page, page_size):
        interval = self.get_interval(keyword)

        # Define the end time as the current time in UTC
        end_time = timezone.now()  # This should already be aware and in UTC
        # Define the start time based on the interval and page size
        start_time = end_time - (interval * page_size * page)

        # Fetch data for the range of times from start_time to end_time
        all_data = list(
            NumberChange.objects.filter(time__range=(start_time, end_time))
            .values("time", "open", "high", "low", "close")
            .order_by("time")
        )

        unique_data = []
        for entry in all_data:
            entry["time"] = int(entry["time"].timestamp())
            if all(
                self.is_valid_number(entry[field])
                for field in ["open", "high", "low", "close"]
            ):
                unique_data.append(entry)

        if not unique_data:
            return {"error": "No data available for the selected timeframe and page."}

        selected_data = self.group_by_interval(unique_data, interval)

        return selected_data

    def get_interval(self, keyword):
        if keyword == "1Min":
            return timedelta(minutes=1)
        if keyword == "5Min":
            return timedelta(minutes=5)
        elif keyword == "1Hour":
            return timedelta(hours=1)
        elif keyword == "1Day":
            return timedelta(days=1)
        return timedelta(minutes=1)

    def group_by_interval(self, data, interval):
        if not data:
            return []

        grouped_data = []
        current_group = []
        current_start_time = data[0]["time"]

        for entry in data:
            entry_time = entry["time"]
            if entry_time < current_start_time + interval.total_seconds():
                current_group.append(entry)
            else:
                if current_group:
                    candle = self.create_candle_from_group(current_group)
                    if candle:
                        grouped_data.append(candle)
                current_group = [entry]
                current_start_time = entry_time

        if current_group:
            candle = self.create_candle_from_group(current_group)
            if candle:
                grouped_data.append(candle)

        return grouped_data

    def create_candle_from_group(self, group):
        if not group:
            return None
        open_price = group[0]["open"]
        close_price = group[-1]["close"]
        high_price = max(entry["high"] for entry in group)
        low_price = min(entry["low"] for entry in group)
        return {
            "time": group[0]["time"],
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
        }

    def is_valid_number(self, value):
        try:
            return (
                value is not None
                and not isinstance(value, str)
                and not isinstance(value, bool)
            )
        except (TypeError, ValueError):
            return False
