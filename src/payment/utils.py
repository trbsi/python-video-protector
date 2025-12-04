# creator balance deducted by platform fee
from decimal import Decimal

from src.payment.enums import PaymentEnum
from src.payment.value_objects.user_balance_value_object import UserBalanceValueObject


def get_creator_balance_in_fiat(coins: Decimal) -> UserBalanceValueObject:
    return UserBalanceValueObject(coins)


def coin_to_fiat(amount_in_coins: Decimal) -> Decimal:
    return amount_in_coins / Decimal(PaymentEnum.COIN_TO_FIAT.value)


def fiat_to_coins(amount_in_fiat: Decimal) -> Decimal:
    return amount_in_fiat * Decimal(PaymentEnum.COIN_TO_FIAT.value)
