from decimal import Decimal, ROUND_HALF_UP

from src.payment.enums import PaymentEnum


class UserBalanceValueObject:
    # commission in fiat
    platform_commission: Decimal
    # balance in fiat
    user_balance: Decimal

    def __init__(self, coins: Decimal):
        self.coins = coins
        self.calculate_payout()

    def calculate_payout(self) -> None:
        coin_to_fiat = Decimal(PaymentEnum.COIN_TO_FIAT.value)
        platform_commission_percentage = Decimal(PaymentEnum.COMMISSION_PERCENTAGE.value)

        balance_in_fiat: Decimal = self.coins / Decimal(coin_to_fiat)

        self.platform_commission: Decimal = balance_in_fiat * Decimal(platform_commission_percentage)
        self.user_balance: Decimal = balance_in_fiat - self.platform_commission

        self.platform_commission = self.platform_commission.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.user_balance = self.user_balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
