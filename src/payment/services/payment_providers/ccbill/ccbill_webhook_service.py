from src.payment.enums import PaymentEnum
from src.payment.value_objects.payment_webhook_value_object import PaymentWebhookValueObject


class CCBillWebhookService():
    # https://ccbill.com/doc/webhooks-user-guide
    def handle_webhook(self, data: dict):
        payment_id = data.get("X-paymentid")
        event_type = data.get("eventType")

        if event_type == "NewSaleSuccess":
            status = PaymentEnum.STATUS_SUCCESS.value
        else:
            status = PaymentEnum.STATUS_FAILED.value

        return PaymentWebhookValueObject(payment_id, status)
