from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("create/", views.DepositRequest.as_view()),
    path("request/", views.GetDepoistRequests.as_view()),
    path("accept/", views.AcceptDepositRequest.as_view()),
    path("disable/", views.DisableDepositRequest.as_view()),
    path("all/", views.GetAllDeposits.as_view()),
    path("history/client/", views.GetDepoistHistoryClient.as_view()),
    path("withdrawEmail/", views.WithdrawEmail.as_view()),
    path("withdrawEmailConfirmation/", views.withdrawEmailConfirmation.as_view()),
    path("withdrawsList/", views.AdminWithdrawsList.as_view()),
    path("clientWithdrawsList/", views.WithdrawsList.as_view()),
    path("withdrawsAnswer/", views.AdminWithdrawsAnswer.as_view()),
    path("buy/", views.Buy.as_view()),
    path("sell/", views.Sell.as_view()),
    path("infoClient/", views.SellAndBuyClient.as_view()),
    path("infoPublic/", views.SellAndBuyPublic.as_view()),
    path("infoAdmin/", views.SellAndBuyAdmin.as_view()),
]
