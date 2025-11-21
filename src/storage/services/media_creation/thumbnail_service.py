import random
import subprocess
import uuid

from src.media.models import Media
from src.storage.services.remote_storage_service import RemoteStorageService
from src.storage.utils import remote_file_path_for_media


class ThumbnailService:

    def __init__(self, remote_storage_service: RemoteStorageService | None = None):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()

    """
    Generate one thumbnail by snapping picture at 10th second
    """

    def snap_thumbnail(
            self,
            media: Media,
            local_file_type: str,
            local_file_path: str,
            local_file_path_directory: str
    ) -> dict:
        output_thumbnail_path = f'{local_file_path_directory}/{uuid.uuid4()}.jpg'

        # 1. Get video duration
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            local_file_path
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        duration = float(result.stdout)

        # 2. Pick a random timestamp
        time_in_seconds = random.uniform(0, duration)

        # 3. Generate thumbnail
        command = [
            'ffmpeg',
            '-ss', str(time_in_seconds),
            '-i', local_file_path,
            '-frames:v', '1',
            '-q:v', '2',
            output_thumbnail_path
        ]
        subprocess.run(command, check=True)

        remote_file_path = remote_file_path_for_media(media, 'jpg', 'thumbnail')
        file_info = self.remote_storage_service.upload_file(
            local_file_type=local_file_type,
            local_file_path=output_thumbnail_path,
            remote_file_path=remote_file_path,
        )

        media.file_thumbnail = file_info
        media.save()

        return {
            'output_thumbnail_path': output_thumbnail_path
        }
