from unittest import TestCase
from unittest.mock import patch, call, ANY

from src.storage.services.sharding.shard_metadata_value_object import ShardMetadataValueObject
from src.storage.services.sharding.sharding_service import ShardingService


class TestSharding(TestCase):
    @patch('src.storage.services.sharding.sharding_service.os.urandom')
    @patch('src.storage.services.sharding.sharding_service.uuid.uuid4')
    @patch('src.storage.services.sharding.sharding_service.secrets.token_bytes')
    @patch('src.storage.services.remote_storage_service.RemoteStorageService')
    @patch('src.media.models.Media')
    @patch('cryptography.hazmat.primitives.ciphers.aead.AESGCM')
    @patch('cryptography.hazmat.primitives.ciphers.aead.AESGCM.generate_key')
    @patch('src.storage.services.sharding.split_video_service.SplitVideoService')
    @patch('pathlib.Path')
    @patch('src.storage.services.local_storage_service.LocalStorageService')
    def test_shard_media(
            self,
            mock_local_storage_service,
            mock_path,
            mock_split_video_service,
            mock_aesgcm_generate_key,
            mock_aesgcm,
            mock_media,
            mock_remote_storage_service,
            mock_token_bytes,
            uuid_mock,
            mock_urandom,
    ):
        seconds_per_video = 10
        # for: shard_value_object.file.read_bytes()
        mock_path.side_effect = [b'xxx', b'yyy', b'aaa', b'bbb']
        # for: self.split_video_service.split_video_by_seconds()
        mock_split_video_service.split_video_by_seconds.return_value = (
            [
                ShardMetadataValueObject(
                    file=mock_path,
                    start_time=0 * seconds_per_video,
                    duration=seconds_per_video,
                ),
                ShardMetadataValueObject(
                    file=mock_path,
                    start_time=1 * seconds_per_video,
                    duration=seconds_per_video,
                ),
                ShardMetadataValueObject(
                    file=mock_path,
                    start_time=2 * seconds_per_video,
                    duration=seconds_per_video,
                ),
                ShardMetadataValueObject(
                    file=mock_path,
                    start_time=3 * seconds_per_video,
                    duration=seconds_per_video,
                )
            ],
            142
        )
        # for: AESGCM.generate_key(bit_length=256)
        mock_aesgcm_generate_key.return_value = b'masterkeymasterkeymasterkey12345'
        # for: self.aesgcm.encrypt()
        mock_aesgcm.encrypt.return_value = b'wrappedmasterkey'
        # for: secrets.token_bytes(12)
        mock_token_bytes.side_effect = [b'wrapwrapnonce', b'a' * 12, b'b' * 12, b'c' * 12, b'd' * 12]
        # for: os.urandom(1)
        mock_urandom.side_effect = [bytes([1]), bytes([2]), bytes([3]), bytes([4])]
        # for: uuid.uuid4()
        uuid_mock.side_effect = ['bd7a2bc7-4537-4a28-8bb3-1ea7d1b4e292', '764148ff-4c0f-49d5-b57c-93d56a074feb',
                                 'fbc4832b-0d73-4979-91db-6d49f3a87d16', '2e0e7dbc-26a0-4200-ba71-75769685a27b']
        # for: self.remote_storage_service.upload_bytes()
        mock_remote_storage_service.upload_bytes.side_effect = [{'file_info': 'file1'}, {'file_info': 'file2'},
                                                                {'file_info': 'file3'}, {'file_info': 'file4'}]

        # for: self.local_storage_service.upload_byte_file()
        mock_local_storage_service.upload_byte_file.return_value = None

        mock_media.id = 111
        mock_media.user_id = 444
        mock_media.file_type = 'video'
        mock_media.file_metadata = {'file_info': 'file1', 'file_path': '/a/b/c'}
        local_file_path = 'test.mp4'

        service = ShardingService(
            remote_storage_service=mock_remote_storage_service,
            split_video_service=mock_split_video_service,
            local_storage_service=mock_local_storage_service,
            aesgcm=mock_aesgcm
        )
        service.shard_media(mock_media, local_file_path)

        mock_aesgcm.encrypt.assert_called_once_with(
            nonce=b'wrapwrapnonce',
            data=b'masterkeymasterkeymasterkey12345',
            associated_data=None
        )

        self.assertEqual(mock_media.nonce, b'wrapwrapnonce')
        self.assertEqual(mock_media.master_key, b'wrappedmasterkey')
        self.assertEqual(
            mock_media.file_metadata,
            {'file_info': 'file1', 'file_path': '/a/b/c', 'total_time_in_seconds': 142}
        )
        self.assertEqual(mock_remote_storage_service.upload_bytes.call_count, 4)

        shard_names = (
            'bd7a2bc7_45370_4a281_8bb3_1ea7d1b4e292.dar.io',
            '764148ff_4c0f1_49d52_b57c_93d56a074feb.dar.io',
            'fbc4832b_0d732_49793_91db_6d49f3a87d16.dar.io',
            '2e0e7dbc_26a03_42004_ba71_75769685a27b.dar.io'
        )
        mock_remote_storage_service.upload_bytes.assert_has_calls(
            [
                call(
                    file_bytes=ANY,
                    remote_file_path=f'video/media/444/shards/111/{shard_names[0]}'
                ),
                call(
                    file_bytes=ANY,
                    remote_file_path=f'video/media/444/shards/111/{shard_names[1]}'
                ),
                call(
                    file_bytes=ANY,
                    remote_file_path=f'video/media/444/shards/111/{shard_names[2]}'
                ),
                call(
                    file_bytes=ANY,
                    remote_file_path=f'video/media/444/shards/111/{shard_names[3]}'
                ),
            ]
        )
        self.assertEqual(
            mock_media.shards_metadata,
            [
                {
                    'nonce': '616161616161616161616161',
                    'shard': shard_names[0],
                    'mask': '01',
                    'storage_metadata': {'file_info': 'file1'},
                    'start_time': 0,
                    'duration': seconds_per_video,
                },
                {
                    'nonce': '626262626262626262626262',
                    'shard': shard_names[1],
                    'mask': '02',
                    'storage_metadata': {'file_info': 'file2'},
                    'start_time': 10,
                    'duration': seconds_per_video,
                },
                {
                    'nonce': '636363636363636363636363',
                    'shard': shard_names[2],
                    'mask': '03',
                    'storage_metadata': {'file_info': 'file3'},
                    'start_time': 20,
                    'duration': seconds_per_video,
                },
                {
                    'nonce': '646464646464646464646464',
                    'shard': shard_names[3],
                    'mask': '04',
                    'storage_metadata': {'file_info': 'file4'},
                    'start_time': 30,
                    'duration': seconds_per_video,
                }
            ]
        )
