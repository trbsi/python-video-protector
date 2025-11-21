from app import settings


class PushNotificationValueObject():
    def __init__(
            self,
            body: str,
            title: str = '',
            user_id: str | None = None,
            url: str | None = None,
    ):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.url = url or settings.APP_URL
