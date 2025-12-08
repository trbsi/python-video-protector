from decimal import Decimal

from protectapp import settings
from src.payment.enums import PaymentEnum
from src.payment.models import PaymentHistory, Package
from src.payment.services.payment_providers.payment_provider_service import PaymentProviderService
from src.payment.value_objects.checkout_value_object import CheckoutValueObject
from src.user.models import User


class BuyPackageService():
    def __init__(self, provider_service: PaymentProviderService | None = None):
        self.payment_provider_service = provider_service or PaymentProviderService()

    def buy_defined_package(self, user: User, package_id: int) -> CheckoutValueObject:
        package = Package.objects.get(id=package_id)

        value_object: CheckoutValueObject = self._create_checkout(
            user=user,
            price=package.price,
            amount=package.amount
        )

        payment_history = PaymentHistory.objects.filter(provider_payment_id=value_object.provider_payment_id).first()
        payment_history.content_object = package
        payment_history.save()

        return value_object

    def buy_custom_package(self, user: User, price: Decimal, amount: Decimal) -> CheckoutValueObject:
        value_object: CheckoutValueObject = self._create_checkout(
            user=user,
            price=price,
            amount=amount
        )

        return value_object

    def _create_checkout(self, user: User, price: Decimal, amount: Decimal) -> CheckoutValueObject:
        payment_history = PaymentHistory.objects.create(
            user=user,
            price=price,
            amount=amount,
            provider=settings.DEFAULT_PAYMENT_PROVIDER,
            provider_payment_id='default_no_id',
            status=PaymentEnum.STATUS_PENDING.value,
        )

        value_object: CheckoutValueObject = self.payment_provider_service.create_checkout(payment_history)
        payment_history.provider_payment_id = value_object.provider_payment_id
        payment_history.save()

        return value_object
