from decimal import Decimal

from src.engagement.models import Comment
from src.inbox.models import Message
from src.media.models import Media
from src.payment.enums import SpendEnum
from src.payment.exceptions import BalanceTooLowException
from src.payment.models import Balance, Spending
from src.user.models import User


class SpendService:
    def get_price_per_object(self, object: Media | Comment | Message):
        if isinstance(object, Media):
            return object.unlock_price

        if isinstance(object, Comment):
            return SpendEnum.COMMENT_COINS.value

        if isinstance(object, Message):
            if object.is_media_message():
                return SpendEnum.MEDIA_MESSAGE_COINS.value
            else:
                return SpendEnum.TEXT_MESSAGE_COINS.value

        return 0

    def spend_comment(self, user: User, comment: Comment) -> Decimal:
        return self._spend(
            spender=user,
            recipient=comment.media.user,
            amount=Decimal(SpendEnum.COMMENT_COINS.value),
            object=comment
        )

    def spend_media_unlock(self, user: User, media: Media) -> Decimal:
        if media.is_image():
            amount = SpendEnum.IMAGE_COINS.value
        elif media.is_video():
            amount = SpendEnum.VIDEO_COINS.value

        return self._spend(spender=user, recipient=media.user, amount=Decimal(amount), object=media)

    def spend_message(self, user: User, message: Message) -> Decimal:
        if message.is_media_message():
            amount = SpendEnum.MEDIA_MESSAGE_COINS.value
        else:
            amount = SpendEnum.TEXT_MESSAGE_COINS.value

        return self._spend(
            spender=user,
            recipient=message.conversation.get_creator(),
            amount=Decimal(amount),
            object=message
        )

    def _spend(
            self,
            spender: User,
            recipient: User,
            amount: Decimal,
            object: Message | Media | Comment
    ) -> Decimal:

        # @TODO what if people start registering as creators and do things for free?
        if spender.is_creator():
            return Decimal(0)

        spender_balance = Balance.objects.get(user=spender)
        recipient_balance = Balance.objects.get(user=recipient)

        if spender_balance.balance < amount:
            raise BalanceTooLowException('Balance too low.')

        spender_balance.balance = spender_balance.balance - amount
        spender_balance.save()

        recipient_balance.balance = recipient_balance.balance + amount
        recipient_balance.save()

        Spending.objects.create(
            by_user=spender,
            on_user=recipient,
            amount=amount,
            content_object=object
        )

        return amount
