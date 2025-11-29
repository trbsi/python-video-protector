from unittest import TestCase
from unittest.mock import patch

from src.storage.services.sharding.sharding_service import ShardingService


class TestSharding(TestCase):
    @patch('src.storage.services.sharding.sharding_service.Path.read_bytes')
    @patch('src.storage.services.sharding.sharding_service.os.urandom')
    @patch('src.storage.services.sharding.sharding_service.uuid.uuid4')
    @patch('src.storage.services.sharding.sharding_service.secrets.token_bytes')
    @patch('src.storage.services.remote_storage_service.RemoteStorageService')
    @patch('src.media.models.Media')
    def test_shard_media(
            self,
            mock_media,
            mock_remote_storage_service,
            mock_token_bytes,
            uuid_mock,
            mock_urandom,
            mock_read_bytes
    ):
        mock_read_bytes.return_value = b'x' * (1024 * 1024)  # 4x256kb
        mock_urandom.side_effect = [bytes([1]), bytes([2]), bytes([3]), bytes([4])]
        mock_token_bytes.side_effect = [b'a' * 12, b'b' * 12, b'c' * 12, b'd' * 12]
        uuid_mock.side_effect = ['bd7a2bc7-4537-4a28-8bb3-1ea7d1b4e292', '764148ff-4c0f-49d5-b57c-93d56a074feb',
                                 'fbc4832b-0d73-4979-91db-6d49f3a87d16', '2e0e7dbc-26a0-4200-ba71-75769685a27b']
        mock_remote_storage_service.upload_bytes.side_effect = [{'file_info': 'file1'}, {'file_info': 'file2'},
                                                                {'file_info': 'file3'}, {'file_info': 'file4'}]

        mock_media.id = 111
        mock_media.user_id = 444
        local_file_path = 'test.mp4'
        service = ShardingService(remote_storage_service=mock_remote_storage_service)
        service.shard_media(mock_media, local_file_path)

        self.assertEqual(
            mock_media.shards_metadata,
            [
                {
                    'nonce': '616161616161616161616161',
                    'shard': 'bd7a2bc7_45370_4a281_8bb3_1ea7d1b4e292.dar.io',
                    'mask': '01',
                    'storage_metadata': {'file_info': 'file1'}
                },
                {
                    'nonce': '626262626262626262626262',
                    'shard': '764148ff_4c0f1_49d52_b57c_93d56a074feb.dar.io',
                    'mask': '02',
                    'storage_metadata': {'file_info': 'file2'}
                },
                {
                    'nonce': '636363636363636363636363',
                    'shard': 'fbc4832b_0d732_49793_91db_6d49f3a87d16.dar.io',
                    'mask': '03',
                    'storage_metadata': {'file_info': 'file3'}
                },
                {
                    'nonce': '646464646464646464646464',
                    'shard': '2e0e7dbc_26a03_42004_ba71_75769685a27b.dar.io',
                    'mask': '04',
                    'storage_metadata': {'file_info': 'file4'}
                }
            ]
        )
        self.assertEqual(mock_remote_storage_service.upload_bytes.call_count, 4)
