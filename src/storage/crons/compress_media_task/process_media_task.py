import os

import bugsnag

from protectapp import settings
from src.notification.services.notification_service import NotificationService
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject
from src.storage.services.compression.compress_media_service import CompressMediaService
from src.storage.services.media_creation.thumbnail_service import ThumbnailService
from src.storage.services.media_creation.trailer_service import TrailerService
from src.storage.services.remote_storage_service import RemoteStorageService


class ProcessMediaTask:
    MEDIA_TYPE_MEDIA = 'media'
    MEDIA_TYPE_INBOX = 'inbox'

    def __init__(
            self,
            remote_storage_service: RemoteStorageService or None = None,
            compress_service: CompressMediaService or None = None,
            thumbnail_service: ThumbnailService or None = None,
            trailer_service: TrailerService or None = None,
    ):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()
        self.compress_service = compress_service or CompressMediaService()
        self.thumbnail_service = thumbnail_service or ThumbnailService()
        self.trailer_service = trailer_service or TrailerService()

    def process_media(
            self,
            media_type: str,
            media_id: int,
            local_file_path: str,
            create_thumbnail: bool,
            create_trailer: bool,
            should_compress_media: bool,
            download_from_remote: bool,
    ) -> None:
        media = None
        if media_type == self.MEDIA_TYPE_INBOX:
            media = Message.objects.get(id=media_id)
        elif media_type == self.MEDIA_TYPE_MEDIA:
            media = Media.objects.get(id=media_id)

        if media is None or media.file_info is None:
            return

        local_file_path_directory = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(local_file_path_directory, exist_ok=True)

        files_to_remove = []
        files_to_remove.append(local_file_path)

        if download_from_remote:
            try:
                # download file from remote
                downloaded_local_file_path = self.remote_storage_service.download_file(
                    file_id=media.file_info.get('file_id'),
                    file_path=media.file_info.get('file_path'),
                    local_file_path_directory=local_file_path_directory
                )
                local_file_path = downloaded_local_file_path
                files_to_remove.append(local_file_path)
            except Exception as e:
                bugsnag.notify(e)
                return  # no point of going further if file cannot be downloaded

        if should_compress_media:
            try:
                # compress file
                compression_result = self.compress_service.handle_compression(
                    media=media,
                    local_file_type=media.file_type,
                    local_file_path=local_file_path,
                    local_file_path_directory=local_file_path_directory
                )
                local_file_path = compression_result.get('output_compressed_file_path')
                files_to_remove.append(local_file_path)
            except Exception as e:
                bugsnag.notify(e)

        # create thumbnail
        if create_thumbnail and media.is_video():
            try:
                thumbnail_result = self.thumbnail_service.snap_thumbnail(
                    media=media,
                    local_file_type=media.file_type,
                    local_file_path=local_file_path,
                    local_file_path_directory=local_file_path_directory,
                )
                files_to_remove.append(thumbnail_result.get('output_thumbnail_path'))
            except Exception as e:
                bugsnag.notify(e)

        # create trailer
        if create_trailer and media.is_video():
            try:
                trailer_result = self.trailer_service.make_trailer(
                    media=media,
                    local_file_type=media.file_type,
                    local_file_path=local_file_path,
                    local_file_path_directory=local_file_path_directory,
                    clip_count=4,
                    trailer_length=6,
                )
                files_to_remove.append(trailer_result.get('output_trailer_file_path'))
                files_to_remove = files_to_remove + trailer_result.get('parts')
            except Exception as e:
                bugsnag.notify(e)

        # remove local files
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)

        # set model as ready
        if isinstance(media, Media):
            media.is_processed = True
            if media.status != MediaEnum.STATUS_SCHEDULE.value:
                media.status = MediaEnum.STATUS_PAID.value
            media.save()

            url = reverse_lazy_admin(object=media, action='changelist', is_full_url=True)
            push_notification = PushNotificationValueObject(body=f'[CONTENT UPLOADED] {url}')
            NotificationService.send_notification(push_notification)
        elif isinstance(media, Message):
            media.is_ready = True
            media.save()
