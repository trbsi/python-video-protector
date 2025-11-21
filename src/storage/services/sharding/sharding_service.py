import secrets
import uuid
from importlib.resources import read_binary

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ShardingService:
    def shard_media(self, local_file_path: str):
        file_bytes = read_binary(local_file_path)
        shard_size = 256 * 1024  # 256kb
        shards = []

        for i in range(0, len(file_bytes), shard_size):
            chunk = file_bytes[i:i + shard_size]
            shards.append(chunk)

        for index, shard in enumerate(shards):
            shard = self.bit_scramble(shard)
            nonce = secrets.token_bytes(16)  # 32 char hex string
            print(f'Nonce: {nonce}')
            key = AESGCM.generate_key(bit_length=256)
            encryption = AESGCM(key)
            encrypted_shard = AESGCM.encrypt(nonce, shard, encryption)
            self.upload_shard(encrypted_shard)

    def bit_scramble(self):
        pass

    def upload_shard(self, encrypted_shard, index: int):
        name = str(uuid.uuid4())
        name = name[0:13] + str(index) + name[14:]
        name = f'{name}.dar.io'
