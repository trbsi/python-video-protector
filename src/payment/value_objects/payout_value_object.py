class PayoutValueObject:
    def __init__(self, provider: str, result: bool):
        self.provider = provider
        self.result = result
