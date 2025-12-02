import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.contrib.auth.models import AnonymousUser

from protectapp import settings
from src.media.models import Media, Unlock
from src.media.services.single_media.media_value_object import MediaValueObject
from src.user.models import User


class SingleMediaService:
    def get_single_media(self, media_id: int, user: User | AnonymousUser) -> MediaValueObject:
        media = Media.objects.get(pk=media_id)
        if user.is_authenticated:
            is_unlocked = Unlock.objects.filter(user=user, media=media).exists()
        else:
            is_unlocked = False

        is_unlocked = True  # @TODO remove this
        master_key = self._decrypt_wrapped_master_key(media)
        # Random 32 bytes
        session_key = os.urandom(32)
        wrapped_master_key_for_client = AESGCM(master_key).encrypt(
            nonce=session_key,
            data=master_key,
            associated_data=None
        )

        return MediaValueObject(
            media=media,
            wrapped_master_key_for_client=wrapped_master_key_for_client,
            is_unlocked=is_unlocked
        )

    def _decrypt_wrapped_master_key(self, media: Media) -> bytes:
        root_key = bytes.fromhex(settings.MEDIA_ROOT_ENCRYPT_KEY)
        decrypted_master_key = (
            AESGCM(root_key).decrypt(
                nonce=media.nonce,
                data=media.master_key,
                associated_data=None
            )
        )

        return decrypted_master_key
