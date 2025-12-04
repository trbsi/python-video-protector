from decimal import Decimal

import bugsnag

from src.payment.enums import PaymentEnum
from src.payment.value_objects.payout_value_object import PayoutValueObject


class CCBillPayoutService:
    def do_payout(self, balance: Decimal) -> PayoutValueObject:
        try:
            # do api calls or whatever
            return PayoutValueObject(
                provider=PaymentEnum.PROVIDER_CCBILL.value,
                result=True
            )
        except Exception as e:
            bugsnag.notify(e)
            return PayoutValueObject(
                provider=PaymentEnum.PROVIDER_CCBILL.value,
                result=False
            )
