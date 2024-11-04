from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("userList/", views.UserList.as_view()),
    path("emailCode/", views.EmailConfirm.as_view()),
    path("sign-up/", views.CreateUser.as_view()),
    path("userSearch/", views.UserSearch.as_view()),
    path("userFullDetails/", views.UserFullDetails.as_view()),
    path("changeStatusUser/", views.ChangeStatusUser.as_view()),
    path("changeCurrnecy/", views.ChangeCurrencyUser.as_view()),
    path("ChangePasswordRequest/", views.ChangePassword.as_view()),
    path("PasswordConfirmation/", views.PasswordConfirmation.as_view()),
]
