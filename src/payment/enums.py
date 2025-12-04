from enum import Enum
from typing import Tuple


class SpendEnum(Enum):
    COMMENT_COINS = 20  # 0.2$
    VIDEO_COINS = 100  # 1$
    IMAGE_COINS = 50  # 0.5$
    TEXT_MESSAGE_COINS = 10  # 0.1$
    MEDIA_MESSAGE_COINS = 100  # 1$

    @staticmethod
    def video_price_in_fiat():
        return SpendEnum.VIDEO_COINS.value / PaymentEnum.COIN_TO_FIAT.value

    @staticmethod
    def image_price_in_fiat():
        return SpendEnum.IMAGE_COINS.value / PaymentEnum.COIN_TO_FIAT.value


class PaymentEnum(Enum):
    COIN_TO_FIAT = 100  # 100 coins = 1$
    COMMISSION_PERCENTAGE = 0.2

    PROVIDER_SEGPAY = 'segpay'
    PROVIDER_EPOCH = 'epoch'
    PROVIDER_CCBILL = 'ccbill'

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_CANCELED = 'canceled'
    STATUS_FAILED = 'failed'

    @staticmethod
    def statuses() -> Tuple:
        return (
            (PaymentEnum.STATUS_PENDING.value, 'Pending'),
            (PaymentEnum.STATUS_SUCCESS.value, 'Success'),
            (PaymentEnum.STATUS_CANCELED.value, 'Canceled'),
            (PaymentEnum.STATUS_FAILED.value, 'Failed'),
        )

    @staticmethod
    def providers() -> Tuple:
        return (
            (PaymentEnum.PROVIDER_SEGPAY.value, 'SegGay'),
            (PaymentEnum.PROVIDER_EPOCH.value, 'Epoch'),
        )
