from django.contrib import admin
from .models import Ticket, TicketAnswer


class TicketAdmin(admin.ModelAdmin):

    list_display = ("title", "description", "date_created")


admin.site.register(Ticket, TicketAdmin)


class TicketAnswerAdmin(admin.ModelAdmin):

    list_display = ("ticket", "userType", "message", "time")


admin.site.register(TicketAnswer, TicketAnswerAdmin)
