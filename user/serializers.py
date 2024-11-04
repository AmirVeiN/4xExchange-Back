from chart.models import ChartPrice
from payments.models import BuyToken, Deposit, SellToken, WithdrawRequest
from ticket.models import Ticket
from .models import EmailCode, User, ChangePasswordEmailConfirmation
from rest_framework import serializers
from ticket.serializers import TicketSerializer
from payments.serializers import (
    BuySerializer,
    GetDepositRequestSerializer,
    SellSerializer,
    WithdrawListSerializer,
)


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "date_joined",
            "user_type",
            "usdt",
            "token",
        )

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%Y-%m-%d %H:%M")


class UserFullDetailsSerializer(serializers.ModelSerializer):

    user_withdraw = serializers.SerializerMethodField()
    user_tickets = serializers.SerializerMethodField()
    user_deposits = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    user_buy = serializers.SerializerMethodField()
    user_sell = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "date_joined",
            "user_type",
            "usdt",
            "token",
            "user_tickets",
            "user_deposits",
            "user_withdraw",
            "user_buy",
            "user_sell",
        )

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%Y-%m-%d %H:%M")

    def get_user_tickets(self, obj):
        tickets = Ticket.objects.filter(created_by=obj.id)
        return TicketSerializer(tickets, many=True).data

    def get_user_deposits(self, obj):
        deposit = Deposit.objects.filter(user=obj.id)
        return GetDepositRequestSerializer(deposit, many=True).data

    def get_user_withdraw(self, obj):
        withdraw = WithdrawRequest.objects.filter(user=obj.id)
        return WithdrawListSerializer(withdraw, many=True).data

    def get_user_buy(self, obj):
        buy = BuyToken.objects.filter(user=obj.id)
        return BuySerializer(buy, many=True).data

    def get_user_sell(self, obj):
        sell = SellToken.objects.filter(user=obj.id)
        return SellSerializer(sell, many=True).data


class ChangePassowrdEmailConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePasswordEmailConfirmation
        fields = ["code"]


class CodeEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCode
        fields = ["code", "email"]


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartPrice
        fields = ["name", "number"]
