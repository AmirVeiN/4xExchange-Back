from django.contrib import admin
from django.urls import path, include
from . import views
from .views import convert_data_to_candles

urlpatterns = [
    path("data/", views.ChartData.as_view()),
    path("detail/", views.ChartDetail.as_view()),
    path("change/", views.ChartChangePrice.as_view()),
    path("volume/", views.ChangeVolume.as_view()),
    path("price-change/", views.PriceChangePercentageAPIView.as_view()),
]
