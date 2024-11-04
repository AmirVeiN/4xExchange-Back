from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from payments.serializers import (
    CreateBuySerializer,
    CreateSellSerializer,
    DepositCreateSerializer,
    DepositRequestAllSerializer,
    DepositRequestCreateSerializer,
    GetAllDepositsSerializer,
    GetDepositRequestSerializer,
    SellAndBuyAdminSerializer,
    SellAndBuyPublicSerializer,
    SellAndBuyClientSerializer,
    WithdrawEmailSerializer,
    WithdrawListSerializer,
    WithdrawRequestSerializer,
)
import random
from user.models import User
from .models import (
    Deposit as DepositModel,
    WithdrawRequest,
    DepositRequest as DepositRequestModel,
)
from user.permissions import IsTypeOneUser
from django.core.mail import send_mail
from django.conf import settings
from .models import WithdrawEmailConfirmation
import random
from .tasks import RequestsClient
from chart.models import ChartPrice, NumberChange

class DepositRequest(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        tetherData = request.data["tether"]

        wallet = request.data["wallet"]

        crypto_type = request.data["crypto_type"]

        serializerRespone = DepositRequestCreateSerializer(
            data={
                "tether": tetherData,
                "wallet": wallet,
                "crypto_type": crypto_type,
            }
        )

        if serializerRespone.is_valid():
            serializerRespone.save(user=request.user)
            return Response(status=status.HTTP_200_OK)

        return Response(serializerRespone.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDepoistRequests(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def get(self, request, format=None):

        deposit = DepositRequestModel.objects.all()

        serializer = DepositRequestAllSerializer(deposit, many=True)

        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptDepositRequest(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        DepositId = request.data["pk"]

        depositReq = DepositRequestModel.objects.get(pk=DepositId)

        serializerRespone = DepositCreateSerializer(
            data={
                "tether": depositReq.tether,
                "wallet": depositReq.wallet,
                "crypto_type": depositReq.crypto_type,
            }
        )

        if serializerRespone.is_valid():
            serializerRespone.save(user=request.user)
            depositReq.delete()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class DisableDepositRequest(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        DepositId = request.data["pk"]

        depositReq = DepositRequestModel.objects.get(pk=DepositId)

        if depositReq:

            depositReq.delete()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetDepoistHistoryClient(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        user = User.objects.get(email=request.user)
        deposit = DepositModel.objects.filter(user=user)
        serializer = GetDepositRequestSerializer(deposit, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllDeposits(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def get(self, request, format=None):

        deposit = DepositModel.objects.all()

        serializer = GetAllDepositsSerializer(deposit, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawEmail(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        req = request.data

        if float(req["withdraw"]) <= request.user.usdt:

            code = random.randint(11111, 99999)

            serializer = WithdrawEmailSerializer(
                data={
                    "code": code,
                    "withdraw": req["withdraw"],
                    "wallet": req["wallet"],
                }
            )

            if serializer.is_valid():

                serializer.save(user=request.user)

                subject = "Withdraw Email Verification"
                message = f"Hi, this is your Code for Withdraw verification. This will expire in 5 minutes - {code}"
                email_from = settings.EMAIL_HOST_USER
                address = [request.user.email]

                send_mail(subject, message, email_from, address)

                return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)


class withdrawEmailConfirmation(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        try:

            exits = WithdrawEmailConfirmation.objects.get(code=request.data["code"])

        except:

            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if exits:

            serializer = WithdrawRequestSerializer(
                data={
                    "tether": exits.withdraw,
                    "status": 1,
                    "wallet": exits.wallet,
                }
            )

            if serializer.is_valid():

                serializer.save(user=request.user)

                return Response(status=status.HTTP_201_CREATED)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class AdminWithdrawsList(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        if request.data["type"] == "All":

            withdraw = WithdrawRequest.objects.all()
            serializer = WithdrawListSerializer(withdraw, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:

            withdraw = WithdrawRequest.objects.filter(status=request.data["type"])
            serializer = WithdrawListSerializer(withdraw, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminWithdrawsAnswer(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        try:
            withdraw = WithdrawRequest.objects.get(id=request.data["id"])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if withdraw.status == 1:

            if request.data["answer"]["value"] == 2:

                user = User.objects.get(email=request.data["user"])
                user.usdt -= request.data["tether"]
                user.save()
                withdraw.status = request.data["answer"]["value"]
                withdraw.admin = request.user
                withdraw.answer = timezone.now()
                withdraw.text = request.data["text"]
                withdraw.save()

                return Response(status=status.HTTP_202_ACCEPTED)

            elif request.data["answer"]["value"] == 3:

                withdraw.status = request.data["answer"]["value"]
                withdraw.admin = request.user
                withdraw.answer = timezone.now()
                withdraw.text = request.data["text"]
                withdraw.save()

                return Response(status=status.HTTP_202_ACCEPTED)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class WithdrawsList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        withdraw = WithdrawRequest.objects.filter(user=request.user)
        serializer = WithdrawListSerializer(withdraw, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Buy(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        try:
            price = NumberChange.objects.latest("id")
            user = User.objects.get(email=request.data["user"])
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        serializer = CreateBuySerializer(data=request.data)
        print("slm2")
        print(request.data)
        if serializer.is_valid():
            print("slm3")
            if (
                request.data["tokenPrice"] == price.close
                and request.data["tether"] / price.close == request.data["tokenRecive"]
            ):
                if (request.data["tether"]) <= user.usdt:
                    user.usdt -= request.data["tether"]
                    user.token += request.data["tether"] / price.close
                    user.save()
                    serializer.save(user=user)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class Sell(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        try:
            price = NumberChange.objects.latest("id")
            user = User.objects.get(email=request.data["user"])

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateSellSerializer(data=request.data)

        if serializer.is_valid():

            if (
                request.data["tokenPrice"] == price.close
                and request.data["tetherRecive"] / price.close == request.data["token"]
            ):
                if (request.data["token"]) <= user.token:
                    user.usdt += request.data["token"] * price.close
                    user.token -= request.data["token"]
                    user.save()
                    serializer.save(user=user)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SellAndBuyClient(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        try:
            user = User.objects.get(id=request.data["id"])

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = SellAndBuyClientSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SellAndBuyPublic(APIView):

    permission_classes = []

    def get(self, request, format=None):

        user = User.objects.all()

        serializer = SellAndBuyPublicSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SellAndBuyAdmin(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def get(self, request, format=None):

        user = User.objects.all()

        serializer = SellAndBuyAdminSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
