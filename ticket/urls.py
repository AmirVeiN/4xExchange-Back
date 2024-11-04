from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("create/", views.TicketCreate.as_view()),
    path("all/", views.TicketClient.as_view()),
    path("admin/ticketList/", views.AdminTicket.as_view()),
    path("admin/ticketAnswer/", views.AdminTicketAnswerCreate.as_view()),
    path("admin/ticketComplete/", views.CompleteTicket.as_view()),
    path("ticketAnswer/", views.ClientTicketAnswerCreate.as_view()),
]
