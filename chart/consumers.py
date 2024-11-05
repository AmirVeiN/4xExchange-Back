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

        end_time = timezone.now()
        start_time = end_time - (interval * page_size * page)

        all_data = list(
            NumberChange.objects.filter(time__range=(start_time, end_time))
            .values("time", "open", "high", "low", "close")
            .order_by("time")
        )

        # Convert datetime to timestamp
        for entry in all_data:
            entry["time"] = int(entry["time"].timestamp())

        # اعمال فیلتر کردن داده‌های پرت
        filtered_data = self.remove_outliers(all_data)

        # اعمال میانگین متحرک
        smoothed_data = self.moving_average(filtered_data)

        # محدود کردن تغییرات قیمت
        clamped_data = self.clamp_price_changes(smoothed_data)

        # گروه‌بندی داده‌ها پس از اعمال تمامی تغییرات
        selected_data = self.group_by_interval(clamped_data, interval)

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

    # فیلتر کردن داده‌های پرت
    def remove_outliers(self, data, threshold=2):
        if len(data) < 2:
            return data

        avg = sum(item["close"] for item in data) / len(data)
        std_dev = (sum((item["close"] - avg) ** 2 for item in data) / len(data)) ** 0.5

        return [item for item in data if abs(item["close"] - avg) <= threshold * std_dev]

    # هموارسازی با میانگین متحرک
    def moving_average(self, data, window_size=5):
        if len(data) < window_size:
            return data
        smoothed_data = []
        for i in range(len(data) - window_size + 1):
            avg = sum(item["close"] for item in data[i:i+window_size]) / window_size
            item = data[i].copy()
            item["close"] = avg
            smoothed_data.append(item)
        return smoothed_data

    # محدود کردن تغییرات قیمت
    def clamp_price_changes(self, data, max_change=0.01):
        if not data:
            return []
        
        clamped_data = [data[0]]
        for i in range(1, len(data)):
            change = data[i]["close"] - clamped_data[-1]["close"]
            if abs(change) > max_change:
                change = max_change if change > 0 else -max_change
            new_close = clamped_data[-1]["close"] + change
            new_entry = data[i].copy()
            new_entry["close"] = new_close
            clamped_data.append(new_entry)
        return clamped_data

    def group_by_interval(self, data, interval):
        if not data:
            return []

        grouped_data = []
        current_group = []
        current_start_time = timezone.datetime.fromtimestamp(data[0]["time"])  # تبدیل به datetime
        previous_close = None

        for entry in data:
            entry_time = timezone.datetime.fromtimestamp(entry["time"])  # تبدیل به datetime
            if entry_time < current_start_time + interval:
                current_group.append(entry)
            else:
                if current_group:
                    candle = self.create_candle_from_group(current_group, previous_close)
                    if candle:
                        grouped_data.append(candle)
                        previous_close = candle["close"]  # ذخیره مقدار close برای کندل بعدی
                current_group = [entry]
                current_start_time = entry_time  # به روز رسانی به زمان جدید

        if current_group:
            candle = self.create_candle_from_group(current_group, previous_close)
            if candle:
                grouped_data.append(candle)

        return grouped_data

    def create_candle_from_group(self, group, previous_close=None):
        if not group:
            return None

        # پیوستگی بین کندل‌ها از طریق مقدار close قبلی
        open_price = previous_close if previous_close is not None else group[0]["open"]
        close_price = group[-1]["close"]
        high_price = max(entry["high"] for entry in group)
        low_price = min(entry["low"] for entry in group)

        # ایجاد کندل با پیوستگی
        return {
            "time": int(group[0]["time"]),  # زمان به timestamp تبدیل می‌شود
            "open": round(open_price, 7),
            "high": round(high_price, 7),
            "low": round(low_price, 7),
            "close": round(close_price, 7),
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

