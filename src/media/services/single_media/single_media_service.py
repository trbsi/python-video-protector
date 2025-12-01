import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from protectapp import settings
from src.media.models import Media, Unlock
from src.user.models import User


class SingleMediaService:
    def get_single_media(self, media_id: int, user: User) -> tuple[Media, bytes, bool]:
        media = Media.objects.get(pk=media_id)
        is_unlocked = Unlock.objects.filter(user=user, media=media).exists()

        master_key = self._decrypt_wrapped_master_key(media)
        # Random 32 bytes
        session_key = os.urandom(32)
        wrapped_master_key_for_client = AESGCM(master_key).encrypt(
            nonce=session_key,
            data=master_key,
            associated_data=None
        )

        return media, wrapped_master_key_for_client, is_unlocked

    def _decrypt_wrapped_master_key(self, media: Media) -> bytes:
        decrypted_master_key = (
            AESGCM(settings.MEDIA_ROOT_ENCRYPT_KEY).decrypt(
                nonce=media.nonce,
                data=media.master_key,
                associated_data=None
            )
        )

        return decrypted_master_key
