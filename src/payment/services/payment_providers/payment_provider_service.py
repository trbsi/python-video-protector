from decimal import Decimal

from app import settings
from src.payment.enums import PaymentEnum
from src.payment.models import PaymentHistory
from src.payment.services.payment_providers.ccbill.ccbill_create_checkout_service import CCBillCreateCheckoutService
from src.payment.services.payment_providers.ccbill.ccbill_payout_service import CCBillPayoutService
from src.payment.services.payment_providers.ccbill.ccbill_webhook_service import CCBillWebhookService
from src.payment.value_objects.checkout_value_object import CheckoutValueObject
from src.payment.value_objects.payment_webhook_value_object import PaymentWebhookValueObject
from src.payment.value_objects.payout_value_object import PayoutValueObject


class PaymentProviderService():
    def __init__(
            self,
            ccbill_create_checkout_service: CCBillCreateCheckoutService | None = None,
            ccbill_webhook_service: CCBillWebhookService | None = None,
            ccbill_payout_service: CCBillPayoutService | None = None,
    ):
        self.default_payment_provider = settings.DEFAULT_PAYMENT_PROVIDER
        self.ccbill_create_checkout_service = ccbill_create_checkout_service or CCBillCreateCheckoutService()
        self.ccbill_webhook_service = ccbill_webhook_service or CCBillWebhookService()
        self.ccbill_payout_service = ccbill_payout_service or CCBillPayoutService()

    def create_checkout(self, payment_history: PaymentHistory) -> CheckoutValueObject:
        if self.default_payment_provider == PaymentEnum.PROVIDER_CCBILL.value:
            return self.ccbill_create_checkout_service.create_checkout(payment_history)

        raise Exception('Payment provider is not supported for checkout.')

    def handle_webook(self, body: dict) -> PaymentWebhookValueObject:
        if self.default_payment_provider == PaymentEnum.PROVIDER_CCBILL.value:
            return self.ccbill_webhook_service.handle_webhook(body)

        raise Exception('Payment provider is not supported for webhook.')

    def do_payout(self, balance: Decimal) -> PayoutValueObject:
        if self.default_payment_provider == PaymentEnum.PROVIDER_CCBILL.value:
            return self.ccbill_payout_service.do_payout(balance)

        raise Exception('Payment provider is not supported for payout.')
