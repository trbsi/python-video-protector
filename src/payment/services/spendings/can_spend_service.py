from src.payment.enums import SpendEnum
from src.payment.models import Balance
from src.user.models import User


class CanSpendService():
    def can_spend(self, user: User, type: str) -> bool:
        # @TODO what if people start registering as creators and do things for free?
        if user.is_creator():
            return True
        
        balance = Balance.get_user_balance(user).balance

        if type == 'text_message' and balance < SpendEnum.TEXT_MESSAGE_COINS.value:
            return False

        if type == 'media_message' and balance < SpendEnum.MEDIA_MESSAGE_COINS.value:
            return False

        if type == 'comment' and balance < SpendEnum.COMMENT_COINS.value:
            return False

        if type == 'media_video' and balance < SpendEnum.VIDEO_COINS.value:
            return False

        if type == 'media_image' and balance < SpendEnum.IMAGE_COINS.value:
            return False

        return True
