from b2sdk.v2 import B2Api, Bucket, FileVersion

from protectapp import settings
from src.storage.init_storage import init_remote_storage


class BackBlazeUploadFileService:
    def upload_file(
            self,
            local_file_path: str,
            remote_file_name: str,
            bucket_name: str = 'default',
            additional_file_info: dict = {}
    ):
        default_bucket_name = settings.STORAGE_CONFIG.get('backblaze').get('bucket_name')
        bucket_name = default_bucket_name if bucket_name == '' else bucket_name
        b2_api: B2Api = init_remote_storage()

        bucket: Bucket = b2_api.get_bucket_by_name(bucket_name)
        result: FileVersion = bucket.upload_local_file(
            local_file=local_file_path,
            file_name=remote_file_name,
            file_info=additional_file_info
        )

        return {
            'file_id': result.id_,
            'file_path': result.file_name,
            'bucket_id': result.bucket_id,
            'bucket_name': bucket_name
        }

    def upload_bytes(
            self,
            file_bytes: bytes,
            remote_file_name: str,
            bucket_name: str = '',
            additional_file_info: dict = {}
    ):
        default_bucket_name = settings.STORAGE_CONFIG.get('backblaze').get('bucket_name')
        bucket_name = default_bucket_name if bucket_name == '' else bucket_name
        b2_api: B2Api = init_remote_storage()

        bucket: Bucket = b2_api.get_bucket_by_name(bucket_name)
        result: FileVersion = bucket.upload_bytes(
            data_bytes=file_bytes,
            file_name=remote_file_name,
            file_info=additional_file_info
        )

        return {
            'file_id': result.id_,
            'file_path': result.file_name,
            'bucket_id': result.bucket_id,
            'bucket_name': bucket_name
        }
