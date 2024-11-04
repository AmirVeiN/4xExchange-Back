from django.contrib import admin
from .models import (
    Deposit,
    WithdrawEmailConfirmation,
    DepositRequest,
    WithdrawRequest,
    BuyToken,
    SellToken,
)

admin.site.register(Deposit)
admin.site.register(WithdrawEmailConfirmation)
admin.site.register(DepositRequest)
admin.site.register(WithdrawRequest)
admin.site.register(BuyToken)
admin.site.register(SellToken)

