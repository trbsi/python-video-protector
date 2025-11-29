import bugsnag

from src.media.enums import MediaEnum
from src.media.models import Media
from src.storage.services.remote_storage_service import RemoteStorageService


class DeleteUserMediaTask:
    def delete_user_media(self, user_id: int):
        remote_storage_service = RemoteStorageService()
        media = Media.objects.filter(user_id=user_id).filter(status=MediaEnum.STATUS_DELETED.value)

        for item in media:
            media_item: Media = item
            try:
                remote_storage_service.delete_file(
                    file_id=media_item.file_metadata.get('file_id'),
                    file_path=media_item.file_metadata.get('file_path')
                )
            except Exception as e:
                bugsnag.notify(e)

            if media_item.file_thumbnail is not None:
                try:
                    remote_storage_service.delete_file(
                        file_id=media_item.file_thumbnail.get('file_id'),
                        file_path=media_item.file_thumbnail.get('file_path')
                    )
                except Exception as e:
                    bugsnag.notify(e)

            if media_item.file_trailer is not None:
                try:
                    remote_storage_service.delete_file(
                        file_id=media_item.file_trailer.get('file_id'),
                        file_path=media_item.file_trailer.get('file_path')
                    )
                except Exception as e:
                    bugsnag.notify(e)

            media_item.delete()
