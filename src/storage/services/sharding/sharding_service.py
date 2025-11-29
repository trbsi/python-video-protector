import os
import secrets
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from protectapp import settings
from src.media.models import Media
from src.storage.services.remote_storage_service import RemoteStorageService
from src.storage.utils import remote_shard_file_path_for_media


class ShardingService:
    def __init__(self, remote_storage_service: None | RemoteStorageService = None):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()

    def shard_media(self, media: Media, local_file_path: str) -> None:
        # Read file
        file_bytes = Path(local_file_path).read_bytes()
        shard_size = 256 * 1024  # 256kb
        shards = []

        # Split file
        for i in range(0, len(file_bytes), shard_size):
            chunk = file_bytes[i:i + shard_size]
            shards.append(chunk)

        # Generate one master key for entire video
        # Root key (must be 32 bytes for AES-256)
        root_key = bytes.fromhex(settings.MEDIA_ROOT_ENCRYPT_KEY)
        aesgcm = AESGCM(root_key)
        # Generate unique nonce for wrapping this master key
        wrap_nonce = secrets.token_bytes(12)
        # Generate per-video master key
        master_key = AESGCM.generate_key(32)
        # Encrypt (wrap) the master key with root key
        wrapped_master_key = aesgcm.encrypt(nonce=wrap_nonce, data=master_key, associated_data=None)

        aesgcm_master = AESGCM(master_key)

        # Scramble and encrypt shard
        shard_metadata = []
        for index, shard in enumerate(shards):
            scrambled_shard, mask = self._scramble_shard(shard)

            nonce = secrets.token_bytes(12)

            encrypted_shard = aesgcm_master.encrypt(nonce=nonce, data=scrambled_shard, associated_data=None)
            shard_name = self._shard_name(index, mask)

            remote_file_info = self._upload_shard(media, encrypted_shard, shard_name)

            shard_metadata.append({
                'nonce': nonce.hex(),
                'shard': shard_name,
                'mask': mask.hex(),
                'storage_metadata': remote_file_info
            })

        # Now store both wrapped_master_key and wrap_nonce in your database @TODO
        media.shards_metadata = shard_metadata
        media.save()

    def _scramble_shard(self, shard: bytes) -> tuple[bytes, bytes]:
        # random 1 byte
        mask = os.urandom(1)
        scrambled = bytearray()

        # shard_byte is 1 byte in collection of bytes in shard
        for shard_byte in shard:
            # shard_byte and mask[0] are integers, do XOR operation
            result = shard_byte ^ mask[0]
            # Rotate left 3 bits
            result = ((result << 3) | (result >> 5)) & 0xFF
            scrambled.append(result)

        return bytes(scrambled), mask

    def _upload_shard(self, media: Media, encrypted_shard: bytes, shard_name: str) -> dict:
        remote_file_path = remote_shard_file_path_for_media(media, shard_name)
        result = self.remote_storage_service.upload_bytes(
            file_bytes=encrypted_shard,
            remote_file_path=remote_file_path
        )
        return result

    def _shard_name(self, shard_index: int, mask: bytes) -> str:
        # e.g. bd7a2bc7-4537-4a28-8bb3-1ea7d1b4e292
        name = str(uuid.uuid4())
        name = name.split('-')

        # append shard_index at the end of 4537
        shard_index_place = 1
        shard_name = name[shard_index_place]
        shard_name = f'{shard_name}{shard_index}'

        # Update uuid
        name[shard_index_place] = shard_name

        # append mask[0](integer) at the end of 4a28
        mask_bit_index_place = 2
        mask_bit_name = name[mask_bit_index_place]
        mask_bit_name = f'{mask_bit_name}{mask[0]}'
        name[mask_bit_index_place] = mask_bit_name

        name = '_'.join(name)
        name = f'{name}.dar.io'

        return name
