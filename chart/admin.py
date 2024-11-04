from django.contrib import admin
from .models import ChartPrice, NumberChange, ScheduledNumberChange, ChangeVolume24

admin.site.register(ChartPrice)
admin.site.register(NumberChange)
admin.site.register(ScheduledNumberChange)
admin.site.register(ChangeVolume24)
