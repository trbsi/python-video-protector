from pathlib import Path

from src.media.models import Media
from src.storage.services.compression.compress_file_service import CompressFileService
from src.storage.services.remote_storage_service import RemoteStorageService
from src.storage.utils import remote_file_path_for_media


class CompressMediaService:
    def __init__(
            self,
            remote_storage_service: RemoteStorageService | None = None,
            compress_file_service: CompressFileService | None = None,
    ):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()
        self.compress_file_service = compress_file_service or CompressFileService()

    def handle_compression(
            self,
            media: Media,
            local_file_type: str,
            local_file_path: str,
            local_file_path_directory: str
    ) -> dict:

        original_file_info = media.file_metadata
        extension = Path(original_file_info.get('file_path')).suffix  # example: .jpg or .mp4
        new_file_name = remote_file_path_for_media(media, extension, media.file_type)

        if isinstance(media, Media):
            new_file_path = remote_file_path_for_media(media, new_file_name)

        # compress file
        if media.is_image():
            self.compress_file_service.compress_image(path=local_file_path)
            output_compressed_file_path = local_file_path
        elif media.is_video():
            output_compressed_file_path = f'{local_file_path_directory}/{new_file_name}'
            self.compress_file_service.compress_video(
                input_path=local_file_path,
                output_path=output_compressed_file_path
            )
        else:
            raise Exception('Unknown media type')

        # upload to remote and replace
        file_info = self.remote_storage_service.upload_file(
            local_file_type=local_file_type,
            local_file_path=output_compressed_file_path,
            remote_file_path=new_file_path
        )

        # update model
        media.file_metadata = file_info
        media.save()

        # remove remote file
        self.remote_storage_service.delete_file(
            file_id=original_file_info.get('file_id'),
            file_path=original_file_info.get('file_path')
        )

        return {
            'output_compressed_file_path': output_compressed_file_path,
        }
