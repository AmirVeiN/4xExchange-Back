from rest_framework import serializers

from user.models import User


from .models import (
    Deposit,
    DepositRequest,
    WithdrawEmailConfirmation,
    WithdrawRequest,
    BuyToken,
    SellToken,
)


class DepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ["tether", "wallet", "crypto_type"]


class DepositRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositRequest
        fields = ["tether", "wallet", "crypto_type"]


class DepositRequestAllSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source="user.email")
    run_at = serializers.SerializerMethodField()
    expiration_at = serializers.SerializerMethodField()

    class Meta:
        model = DepositRequest
        fields = [
            "pk",
            "user_email",
            "tether",
            "crypto_type",
            "wallet",
            "run_at",
            "expiration_at",
        ]

    def get_run_at(self, obj):
        return obj.run_at.strftime("%Y-%m-%d %H:%M")

    def get_expiration_at(self, obj):
        return obj.expiration_at.strftime("%Y-%m-%d %H:%M")


class GetDepositRequestSerializer(serializers.ModelSerializer):

    time = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = ["tether", "crypto_type", "wallet", "time"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class GetAllDepositsSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source="user.email")
    time = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = ["user_email", "tether", "crypto_type", "wallet", "time"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class WithdrawEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawEmailConfirmation
        fields = ["code", "withdraw", "wallet"]


class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = ["tether", "status", "wallet"]


class WithdrawListSerializer(serializers.ModelSerializer):

    user = serializers.EmailField(source="user.email")
    time = serializers.SerializerMethodField()

    class Meta:
        model = WithdrawRequest
        fields = ["id", "user", "tether", "time", "status", "wallet", "text"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class CreateBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyToken
        fields = ["tether", "tokenRecive", "tokenPrice"]


class CreateSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellToken
        fields = ["tetherRecive", "token", "tokenPrice"]


class BuySerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email")
    time = serializers.SerializerMethodField()

    class Meta:
        model = BuyToken
        fields = ["user", "tether", "tokenRecive", "tokenPrice", "time"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class SellSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email")
    time = serializers.SerializerMethodField()

    class Meta:
        model = SellToken
        fields = ["user", "tetherRecive", "token", "tokenPrice", "time"]

    def get_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M")


class BuyPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = BuyToken
        fields = ["tether", "tokenRecive"]


class SellPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = SellToken
        fields = ["tetherRecive", "token"]


class SellAndBuyClientSerializer(serializers.ModelSerializer):

    buy = serializers.SerializerMethodField()
    sell = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["buy", "sell"]

    def get_buy(self, obj):
        buy = BuyToken.objects.filter(user=obj.id)
        return BuySerializer(buy, many=True).data

    def get_sell(self, obj):
        sell = SellToken.objects.filter(user=obj.id)
        return SellSerializer(sell, many=True).data


class SellAndBuyPublicSerializer(serializers.ModelSerializer):

    buy = serializers.SerializerMethodField()
    sell = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["buy", "sell"]

    def get_buy(self, obj):
        buy = BuyToken.objects.all()
        return BuyPublicSerializer(buy, many=True).data

    def get_sell(self, obj):
        sell = SellToken.objects.all()
        return SellPublicSerializer(sell, many=True).data


class SellAndBuyAdminSerializer(serializers.ModelSerializer):

    buy = serializers.SerializerMethodField()
    sell = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["buy", "sell"]

    def get_buy(self, obj):
        buy = BuyToken.objects.all()
        return BuySerializer(buy, many=True).data

    def get_sell(self, obj):
        sell = SellToken.objects.all()
        return SellSerializer(sell, many=True).data
