from src.media.models import Media


class MediaValueObject:
    def __init__(
            self,
            media: Media,
            wrapped_master_key_for_client: bytes,
            is_unlocked: bool,
    ):
        self.media = media
        self.wrapped_master_key_for_client = wrapped_master_key_for_client
        self.is_unlocked = is_unlocked
