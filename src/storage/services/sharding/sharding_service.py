import os
import secrets
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ShardingService:
    def shard_media(self, local_file_path: str):
        # Read file
        file_bytes = Path(local_file_path).read_bytes()
        shard_size = 256 * 1024  # 256kb
        shards = []

        # Split file
        for i in range(0, len(file_bytes), shard_size):
            chunk = file_bytes[i:i + shard_size]
            shards.append(chunk)

        # Generate one master key for entire video
        master_key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(master_key)

        # Scramble and encrypt shard
        shard_metadata = []
        for index, shard in enumerate(shards):
            scrambled_shard, mask = self._scramble_shard(shard)

            nonce = secrets.token_bytes(12)

            encrypted_shard = aesgcm.encrypt(nonce=nonce, data=scrambled_shard, associated_data=None)
            shard_name = self._shard_name(index, mask)

            self._upload_shard(encrypted_shard, shard_name)

            shard_metadata.append({
                'nonce': nonce.hex(),
                'shard': shard_name,
                'mask': mask.hex(),
            })

        return shard_metadata

    def _scramble_shard(self, shard: bytes) -> tuple[bytes, bytes]:
        # random 1 byte
        mask = os.urandom(1)
        scrambled = bytearray()

        for shard_byte in shard:
            # XOR integers
            result = shard_byte ^ mask[0]
            # Rotate left 3 bits
            result = ((result << 3) | (result >> 5)) & 0xFF
            scrambled.append(result)

        return bytes(scrambled), mask

    def _upload_shard(self, encrypted_shard: bytes, shard_name: str):
        pass

    def _shard_name(self, shard_index: int, mask: bytes) -> str:
        # e.g. bd7a2bc7-4537-4a28-8bb3-1ea7d1b4e292
        name = str(uuid.uuid4())
        print(name)
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
