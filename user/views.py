import random
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from chart.models import ChartPrice
from payments.models import Deposit
from ticket.models import Ticket
from user.models import EmailCode, User, ChangePasswordEmailConfirmation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from user.permissions import IsTypeOneUser
from .serializers import (
    ChangePassowrdEmailConfirmationSerializer,
    CodeEmailSerializer,
    PriceSerializer,
    UserFullDetailsSerializer,
    UserSerializer,
)
from ticket.serializers import TicketSerializer
from payments.serializers import GetDepositRequestSerializer
from django.core.mail import send_mail
from django.utils import timezone


class EmailConfirm(APIView):

    permission_classes = []

    def post(self, request, format=None):

        code = random.randint(11111, 99999)

        serializer = CodeEmailSerializer(
            data={
                "code": code,
                "email": request.data["email"],
            }
        )

        if serializer.is_valid():

            serializer.save()

            subject = "Email Verification"
            message = f"Hi, this is your Code for verification account. This will expire in 5 minutes - {code}"
            email_from = settings.EMAIL_HOST_USER
            address = [request.data["email"]]

            send_mail(subject, message, email_from, address)

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateUser(APIView):

    permission_classes = []

    def post(self, request, format=None):

        try:

            exits = EmailCode.objects.get(code=request.data["code"])

        except:

            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if exits:

            user = User.objects.create(
                email=request.data["email"],
                username=request.data["username"],
                is_superuser=False,
                is_staff=False,
                is_active=True,
                user_type=3,
            )

            user.set_password(request.data["password"])
            user.save()

            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class UserList(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def get(self, request):

        current_user = request.user

        users = User.objects.exclude(id=current_user.id)

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSearch(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        current_user = request.user
        email_query = request.data["search"]

        users = User.objects.exclude(id=current_user.id).filter(
            Q(email__icontains=email_query)
        )

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserFullDetails(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        user = User.objects.get(id=request.data["id"])

        serializer = UserFullDetailsSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeStatusUser(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        user = User.objects.get(id=request.data["id"])

        user.user_type = request.data["status"]["value"]

        user.save()

        return Response(status=status.HTTP_200_OK)


class ChangeCurrencyUser(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        try:

            user = User.objects.get(email=request.data["user"])

        except:

            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.data["currency"]["value"] == "usdt":

            user.usdt = request.data["amount"]
            user.save()
            return Response(status=status.HTTP_200_OK)

        elif request.data["currency"]["value"] == "token":

            user.token = request.data["amount"]
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):

    permission_classes = []

    def post(self, request, format=None):

        try:
            user = User.objects.get(email=request.data["email"])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        code = random.randint(11111, 99999)

        serializer = ChangePassowrdEmailConfirmationSerializer(
            data={
                "code": code,
            }
        )

        if serializer.is_valid():

            serializer.save(user=user)

            subject = "Change Password Email Verification"
            message = f"Hi, this is your Code for ChangePassword verification. This will expire in 5 minutes - {code}"
            email_from = settings.EMAIL_HOST_USER
            address = [user.email]

            send_mail(subject, message, email_from, address)

            return Response(status=status.HTTP_200_OK)


class PasswordConfirmation(APIView):

    permission_classes = []

    def post(self, request, format=None):

        try:

            exits = ChangePasswordEmailConfirmation.objects.get(
                code=request.data["code"]
            )

        except:

            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if exits:

            user = User.objects.get(email=exits.user)
            user.set_password = request.data["password"]
            user.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

