import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.contrib.auth.models import AnonymousUser

from protectapp import settings
from src.media.models import Media, Unlock
from src.media.services.single_media.media_value_object import MediaValueObject
from src.user.models import User


class SingleMediaService:

    def get_single_media(self, media_id: int, user: User | AnonymousUser) -> MediaValueObject:
        media = Media.objects.filter(id=media_id).filter(is_processed=True).get()
        if user.is_authenticated:
            is_unlocked = Unlock.objects.filter(user=user, media=media).exists()
        else:
            is_unlocked = False

        is_unlocked = True  # @TODO remove this
        master_key = self._decrypt_wrapped_master_key(media)
        # Random 32 bytes
        session_key = os.urandom(32)
        # standard 12-byte AES-GCM nonce
        wrap_nonce = os.urandom(12)
        wrapped_master_key_for_client = AESGCM(session_key).encrypt(
            nonce=wrap_nonce,
            data=master_key,
            associated_data=None
        )

        return MediaValueObject(
            media=media,
            wrapped_master_key=wrapped_master_key_for_client,
            wrap_nonce=wrap_nonce,
            session_key=session_key,
            is_unlocked=is_unlocked
        )

    def _decrypt_wrapped_master_key(self, media: Media) -> bytes:
        root_key = bytes.fromhex(settings.MEDIA_ROOT_ENCRYPT_KEY)
        aesgcm = AESGCM(root_key)

        return (
            aesgcm.decrypt(
                nonce=media.nonce,
                data=media.master_key,
                associated_data=None
            )
        )
