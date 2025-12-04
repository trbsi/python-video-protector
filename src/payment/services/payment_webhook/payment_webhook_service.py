from src.payment.models import PaymentHistory, Balance
from src.payment.services.payment_providers.payment_provider_service import PaymentProviderService
from src.payment.value_objects.payment_webhook_value_object import PaymentWebhookValueObject


class PaymentWebhookService:
    def __init__(self, provider_service: PaymentProviderService | None = None):
        self.payment_provider_service = provider_service or PaymentProviderService()

    # @TODO finish webhook
    def handle_webook(self, body: dict):
        payment_status: PaymentWebhookValueObject = self.payment_provider_service.handle_webook(body)

        payment_history: PaymentHistory = (
            PaymentHistory
            .objects
            .get(provider_payment_id=payment_status.provider_payment_id)
        )
        payment_history.status = payment_status.status
        payment_history.save()

        if payment_status.is_success():
            balance = Balance.objects.get(user=payment_history.user)
            balance.balance += payment_history.amount
            balance.save()
