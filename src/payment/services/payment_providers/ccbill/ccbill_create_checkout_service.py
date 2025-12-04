import hashlib
import uuid

from app import settings
from src.payment.models import PaymentHistory
from src.payment.value_objects.checkout_value_object import CheckoutValueObject


class CCBillCreateCheckoutService:

    # https://ccbill.com/doc/flexforms-quick-start-guide
    # https://ccbill.com/doc/dynamic-pricing-user-guide
    def create_checkout(self, payment_history: PaymentHistory) -> CheckoutValueObject:
        currency = settings.DEFAULT_CURRENCY
        payment_id = str(uuid.uuid4())

        if currency == 'USD':
            currency_code = '840'
        else:
            raise Exception(f'Currency code is not set: {currency}')

        ccbill = settings.CCBILL_SETTINGS

        amount = payment_history.price
        client_account_number = ccbill.get('account_number')
        client_subaccount_number = ccbill.get('subaccount_number')
        flex_form_id = ccbill.get('flex_form_id')
        # salt can be found at: Client Admin → Account Info → Sub-account Management → View Salts
        salt = ccbill.get('salt')
        initial_price = str(amount)
        initial_period = "30"

        to_hash = initial_price + initial_period + currency_code + salt
        form_digest = hashlib.md5(to_hash.encode("utf-8")).hexdigest()

        if settings.DEBUG:
            base_url = 'https://sandbox-api.ccbill.com'
        else:
            base_url = 'https://api.ccbill.com'
            
        redirect_url = (
            f"{base_url}/wap-frontflex/flexforms/{flex_form_id}?"
            f"clientAccnum={client_account_number}&clientSubacc={client_subaccount_number}&"
            f"initialPrice={initial_price}&initialPeriod={initial_period}&"
            f"currencyCode={currency_code}&formDigest={form_digest}&X-paymentid={payment_id}"
        )

        return CheckoutValueObject(redirect_url, payment_id)
