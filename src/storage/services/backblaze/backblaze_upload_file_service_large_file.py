import hashlib
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from b2sdk.v2 import B2Api, Bucket

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
        config = settings.STORAGE_CONFIG['backblaze']
        b2_api: B2Api = init_remote_storage()
        bucket_name = config['default_bucket_name'] if bucket_name == 'default' else bucket_name

        bucket: Bucket = b2_api.get_bucket_by_name(bucket_name)

        result = self.large_file_upload(b2_api=b2_api, file_path=local_file_path, file_name=remote_file_name,
                                        bucket=bucket)
        # result: FileVersion = bucket.upload_local_file(
        #     local_file=local_file_path,
        #     file_name=remote_file_name,
        #     file_info=additional_file_info
        # )

        return {
            'file_id': result.id_,
            'file_name': result.file_name,
            'bucket_id': result.bucket_id,
            'bucket_name': bucket_name
        }

    def large_file_upload(self, b2_api: B2Api, bucket: Bucket, file_path: str, file_name: str):

        part_size = 10 * 1024 * 1024  # 50 MB
        part_number = 1
        shas = []

        # Start large file upload
        file_info = bucket.api.session.start_large_file(bucket_id=bucket.id_, file_name=file_name,
                                                        content_type="video/mp4", file_info={})
        file_id = file_info["fileId"]

        def upload_part_worker(file_id, part_number, data, bucket, sha1):

            bucket.api.session.upload_part(
                file_id=file_id,
                part_number=part_number,
                content_length=len(data),
                sha1_sum=sha1,
                input_stream=BytesIO(data)
            )

        with open(file_path, "rb") as f, ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            while chunk := f.read(part_size):
                sha1 = hashlib.sha1(chunk).hexdigest()
                shas.append(sha1)
                futures.append(
                    executor.submit(upload_part_worker, file_id, part_number, chunk, bucket, sha1)
                )
                part_number += 1

            # Wait for all parts to finish
            for future in futures:
                future.result()

        # Finalize large file
        bucket.api.session.finish_large_file(file_id, shas)
        return file_info
