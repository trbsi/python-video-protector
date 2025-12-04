from django.contrib import admin
from unfold.admin import ModelAdmin

from src.payment.models import PaymentHistory, Balance, Spending


@admin.register(Balance)
class BalanceAdmin(ModelAdmin):
    list_display = ('id', 'user', 'balance_in_coins', 'balance_in_fiat')
    list_filter = ('created_at',)
    readonly_fields = ('balance_in_fiat',)

    @admin.display(description='Balance in fiat')
    def balance_in_fiat(self, balance):
        return balance.get_balance_as_string()

    @admin.display(description='Balance in fiat')
    def balance_in_coins(self, balance):
        return balance.balance


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(ModelAdmin):
    list_display = ('id', 'user', 'amount', 'provider', 'status')


@admin.register(Spending)
class SpendingAdmin(ModelAdmin):
    list_display = ('id', 'by_user', 'on_user', 'amount_in_coins', 'amount_in_fiat', 'content_object')
    readonly_fields = ('amount_in_fiat', 'content_object')

    @admin.display(description='Amount in fiat')
    def amount_in_fiat(self, spending: Spending):
        return spending.amount_for_creator()

    @admin.display(description='Amount in coins')
    def amount_in_coins(self, spending: Spending):
        return spending.amount_for_user()
