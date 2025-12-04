class CheckoutValueObject:
    def __init__(self, redirect_url: str, provider_payment_id: str) -> None:
        self.redirect_url = redirect_url
        self.provider_payment_id = provider_payment_id
