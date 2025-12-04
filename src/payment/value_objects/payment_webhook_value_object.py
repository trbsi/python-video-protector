from src.payment.enums import PaymentEnum


class PaymentWebhookValueObject:
    def __init__(self, provider_payment_id: str, status: str):
        self.provider_payment_id = provider_payment_id
        self.status = status

    def is_success(self):
        return self.status == PaymentEnum.STATUS_SUCCESS.value
