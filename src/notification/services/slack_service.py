import bugsnag
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app import settings
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject


class SlackService:
    @staticmethod
    def send(notification: PushNotificationValueObject) -> None:
        if notification.user_id is not None:
            return
        
        client = WebClient(token=settings.SLACK_BOT_TOKEN)
        try:
            client.chat_postMessage(
                channel=settings.SLACK_CHANNEL_ID,
                text=notification.body
            )
        except SlackApiError as e:
            bugsnag.notify(e)
