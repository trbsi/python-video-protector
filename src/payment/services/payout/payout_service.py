import bugsnag

from src.payment.models import Balance, Payout
from src.payment.services.payment_providers.payment_provider_service import PaymentProviderService
from src.payment.utils import get_creator_balance_in_fiat
from src.user.models import User


class PayoutService:
    MIN_PAYOUT = 10  # in fiat currency

    def __init__(self, payment_provider_service: PaymentProviderService | None = None):
        self.payment_provider_service = payment_provider_service or PaymentProviderService()

    def do_payout(self) -> None:
        users = User.objects.all()
        for user in users:
            try:
                admin = User.get_admin()
                balance: Balance = Balance.objects.get(user=user)
                balance_for_payout = get_creator_balance_in_fiat(balance.balance)
                if balance_for_payout.user_balance < self.MIN_PAYOUT:
                    return

                payout_value_object = self.payment_provider_service.do_payout(balance_for_payout.user_balance)
                if payout_value_object.result == True:
                    # User payout
                    Payout.objects.create(
                        user=user,
                        amount=balance_for_payout.user_balance,
                        provider=payout_value_object.provider,
                    )

                    # platform payout
                    Payout.objects.create(
                        user=admin,
                        amount=balance_for_payout.platform_commission,
                        provider=payout_value_object.provider,
                    )

                    balance.balance = 0
                    balance.save()
            except Exception as e:
                bugsnag.notify(e)
