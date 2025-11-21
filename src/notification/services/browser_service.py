import json

import bugsnag
from django.templatetags.static import static
from pywebpush import webpush, WebPushException

from app import settings
from src.core.utils import full_url_for_path
from src.notification.models import WebPushSubscription
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject


class BrowserService:
    @staticmethod
    def send(notification: PushNotificationValueObject) -> None:
        if notification.user_id is None:
            return

        web_push_notification = WebPushSubscription.objects.filter(user_id=notification.user_id).all()
        if web_push_notification.count() == 0:
            return

        for single_notification in web_push_notification:
            try:
                payload = {
                    "title": notification.title,
                    "body": notification.body,
                    "url": notification.url,
                    "icon": full_url_for_path(static('images/icon-192.png')),
                    "badge": full_url_for_path(static('images/push_badge.png')),
                }
                claims = {
                    "sub": settings.WEB_PUSH_SUBJECT
                }
                webpush(
                    subscription_info=single_notification.subscription,
                    data=json.dumps(payload),
                    vapid_private_key=settings.WEB_PUSH_PRIVATE_KEY,
                    vapid_claims=claims,
                )
            except WebPushException as e:
                if e.response.status_code == 410:
                    single_notification.delete()
                bugsnag.notify(e)
            except Exception as e:
                bugsnag.notify(e)
