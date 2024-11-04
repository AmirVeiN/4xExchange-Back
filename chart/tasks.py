from celery import shared_task
from .models import ChartPrice, NumberChange
import random
from datetime import datetime, timezone


@shared_task
def change_number(chart_price_id, new_number):
    chart_price = ChartPrice.objects.get(id=chart_price_id)
    chart_price.number = new_number
    chart_price.save()

def create_random_candle(open_price, close):
    high_percentage = random.uniform(0.0001, 0.00001)
    low_percentage = random.uniform(0.0001, 0.00001)
    close_percentage = random.uniform(-0.0001, 0.0001)

    high_price = close + high_percentage
    low_price = close - low_percentage
    close_price = close + close_percentage

    return {
        "time": int(datetime.now(timezone.utc).timestamp()),
        "open": round(open_price, 7),
        "high": round(high_price, 7),
        "low": round(low_price, 7),
        "close": round(close_price, 7),
    }


@shared_task
def create_number_change():
    try:
        chart_price = ChartPrice.objects.get(name="token")
        last_candle = (
            NumberChange.objects.filter(my_model=chart_price).order_by("-time").first()
        )
        close_price = chart_price.number
        open_price = last_candle.close

        candle = create_random_candle(open_price, close_price)

        NumberChange.objects.create(
            my_model=chart_price,
            value=candle["close"],
            time=datetime.fromtimestamp(candle["time"], timezone.utc),
            open=candle["open"],
            high=candle["high"],
            low=candle["low"],
            close=candle["close"],
        )

    except ChartPrice.DoesNotExist:
        print(f"ChartPrice with name 'token' does not exist.")
    except Exception as e:
        print(f"An error occurred in create_number_change: {e}")

