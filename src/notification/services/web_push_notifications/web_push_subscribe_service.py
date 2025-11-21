from src.notification.models import WebPushSubscription
from src.user.models import User


class WebPushSubscribeService:
    def push_subscribe(self, user: User, subscription: dict) -> None:
        WebPushSubscription.objects.create(user=user, subscription=subscription)
