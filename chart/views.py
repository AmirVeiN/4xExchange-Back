from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ChartDataSerializers,
    ChartChangePriceSerializer,
    ChartDetailSerializers,
    TemporaryChartDataSerializer,
)
from .models import NumberChange, ScheduledNumberChange
from rest_framework.permissions import IsAuthenticated
from .models import ChartPrice, ChangeVolume24
from user.permissions import IsTypeOneUser
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
import random
from django.http import HttpResponse
from django.utils import timezone

class ChartData(APIView):

    permission_classes = []

    def get(self, request, format=None):

        chart = NumberChange.objects.all()
        serializer = ChartDataSerializers(chart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChartDetail(APIView):

    permission_classes = []

    def get(self, request, format=None):

        data = ChartPrice.objects.get(name="token")
        serializer = ChartDetailSerializers(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChartChangePrice(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        print(request.data)

        serializer = ChartChangePriceSerializer(data=request.data)

        if serializer.is_valid():
            model = ChartPrice.objects.get(name="token")
            serializer.save(my_model=model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):

        chart = ScheduledNumberChange.objects.all()
        serializer = TemporaryChartDataSerializer(chart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeVolume(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        try:
            volume = ChangeVolume24.objects.get(name="volume")

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        volume.number = request.data["volume"]
        volume.save()
        return Response(status=status.HTTP_202_ACCEPTED)


def convert_data_to_candles(request):
    try:
        chart_data = list(NumberChange.objects.values("time", "value").order_by("time"))

        if not chart_data:
            return HttpResponse(
                "خطا: داده‌های چارت خالی هستند یا مشکلی در دریافت داده‌ها رخ داده است."
            )

        candles = convert_to_candles(chart_data, timedelta(minutes=1))

        for candle in candles:
            NumberChange.objects.create(
                my_model=ChartPrice.objects.first(),
                value=candle["close"],
                time=datetime.fromtimestamp(candle["time"]),
                open=candle["open"],
                high=candle["high"],
                low=candle["low"],
                close=candle["close"],
            )

        return HttpResponse(
            "تبدیل داده‌ها به کندل‌ها با موفقیت انجام شد و در پایگاه داده ذخیره شدند."
        )

    except Exception as e:
        return HttpResponse(f"خطا در تبدیل داده‌ها به کندل‌ها: {str(e)}")

def convert_to_candles(data, time_delta):
    candles = []
    start_time = None
    current_candle_data = []
    previous_close_price = None

    for entry in data:
        time = entry["time"]
        value = entry["value"]

        if start_time is None:
            start_time = time
            current_candle_data.append(value)
            continue

        if time - start_time >= time_delta:
            close_price = sum(current_candle_data) / len(current_candle_data)
            open_price = previous_close_price if previous_close_price else close_price

            # استفاده از مقدار حداقل و حداکثر داده‌ها برای high و low
            high_price = max(current_candle_data)  # بالاترین مقدار واقعی
            low_price = min(current_candle_data)   # پایین‌ترین مقدار واقعی

            candles.append(
                {
                    "time": int(start_time.timestamp()),
                    "open": round(open_price, 7),
                    "high": round(high_price, 7),
                    "low": round(low_price, 7),
                    "close": round(close_price, 7),
                }
            )

            previous_close_price = close_price
            start_time = time
            current_candle_data = [value]
        else:
            current_candle_data.append(value)

    if current_candle_data:
        close_price = sum(current_candle_data) / len(current_candle_data)
        open_price = previous_close_price if previous_close_price else close_price

        high_price = max(current_candle_data)
        low_price = min(current_candle_data)

        candles.append(
            {
                "time": int(start_time.timestamp()),
                "open": round(open_price, 7),
                "high": round(high_price, 7),
                "low": round(low_price, 7),
                "close": round(close_price, 7),
            }
        )

    return candles


class PriceChangePercentageAPIView(APIView):
    def get(self, request, format=None):
        # تعداد داده‌های مورد نیاز برای ۲۴ ساعت گذشته
        required_data_count = 1440

        # دریافت آخرین ۱۴۴۰ داده با ترتیب زمانی صعودی
        last_24_hours_data = NumberChange.objects.order_by('-time')[:required_data_count][::-1]

        # اگر داده کافی وجود دارد
        if len(last_24_hours_data) == required_data_count:
            # محاسبه میانگین ۱۰ دقیقه اول و ۱۰ دقیقه آخر
            initial_prices = [item.value for item in last_24_hours_data[:10]]
            final_prices = [item.value for item in last_24_hours_data[-10:]]
            
            initial_avg = sum(initial_prices) / len(initial_prices)
            final_avg = sum(final_prices) / len(final_prices)

            # محاسبه درصد تغییر بر اساس میانگین اولیه و نهایی
            try:
                change_percentage = ((final_avg - initial_avg) / initial_avg) * 100
            except ZeroDivisionError:
                change_percentage = 0

            # اعمال ضریب کاهش برای کاهش مقدار نهایی درصد تغییر
            adjustment_factor = 0.6  # ضریب کاهش برای کاهش ۴۰ درصدی
            adjusted_change_percentage = change_percentage * adjustment_factor

            # تعیین وضعیت تغییر قیمت
            change_status = "high" if adjusted_change_percentage > 0 else "low" if adjusted_change_percentage < 0 else "dont"

            result = {
                'initial_avg_price': round(initial_avg, 2),
                'final_avg_price': round(final_avg, 2),
                'change_percentage': round(adjusted_change_percentage, 2),  # درصد تغییر کاهش یافته
                'change_status': change_status
            }

            return Response(result)
        else:
            return Response({"error": "Not enough data available for a stable estimate."}, status=404)
