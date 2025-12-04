import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from protectapp import settings
from src.core.management.commands.base_command import BaseCommand
from src.media.models import Media


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("media_id", type=int)

    def handle(self, *args, **options):
        media_id = options["media_id"]
        media = Media.objects.get(pk=media_id)
        wrapped_master_key = media.master_key
        wrap_nonce = media.nonce
        shards_metadata = media.shards_metadata

        # Decrypt wrapped_master_key
        aes = AESGCM(bytes.fromhex(settings.MEDIA_ROOT_ENCRYPT_KEY))
        master_key = aes.decrypt(nonce=wrap_nonce, data=wrapped_master_key, associated_data=None)

        aes_master = AESGCM(master_key)

        # find files in directory
        path = os.path.join(settings.MEDIA_ROOT, 'temp')
        path = os.path.join(settings.BASE_DIR, 'temp')
        folder = os.scandir(path)

        new_file_bytes = bytearray()
        shards_list = []

        for file in folder:
            if not file.is_file() or not file.name.endswith('dar.io'):
                continue

            # get shard_index and shard_mask
            original_shard_name = file.name
            shard_name = file.name.split('_')
            shard_index = shard_name[1]
            mask = shard_name[2]

            shard_index = int(shard_index[4:])
            mask = int(mask[4:])

            # Append info to the list
            shards_list.append({
                'shard_index': shard_index,
                'mask': mask,
                'original_shard_name': original_shard_name,
            })

        # Sort by shard_index
        shards_list.sort(key=lambda shard: shard['shard_index'])

        for shard in shards_list:
            mask = shard.get('mask')
            original_shard_name = shard.get('original_shard_name')

            # get file bytes
            shard_path = os.path.join(settings.MEDIA_ROOT, 'temp', original_shard_name)
            encrypted_file_bytes = Path(shard_path).read_bytes()

            # get file nonce
            file_nonce = self._get_file_nonce(shards_metadata=shards_metadata, shard_name=original_shard_name)

            # decrypt encrypted shard
            decrypted_file_bytes = aes_master.decrypt(nonce=file_nonce, data=encrypted_file_bytes, associated_data=None)

            shard_bytes = bytearray()
            for byte in decrypted_file_bytes:
                # Revert rotation
                result = ((byte >> 3) | (byte << 5)) & 0xFF
                # Revert XOR
                result = result ^ mask
                new_file_bytes.append(result)
                shard_bytes.append(result)

            new_file = f'{path}/{original_shard_name}.mp4'
            with open(new_file, 'wb') as f:
                f.write(bytes(shard_bytes))

        # Save new file
        new_file = f'{path}/original.mp4'
        with open(new_file, 'wb') as f:
            f.write(bytes(new_file_bytes))

        self.success('DONE')

    def _get_file_nonce(self, shards_metadata: list, shard_name: str) -> bytes:
        for metadata in shards_metadata:
            if shard_name == metadata.get('shard'):
                return bytes.fromhex(metadata.get('nonce'))

        raise Exception(f'Metadata not found for {shard_name}')
