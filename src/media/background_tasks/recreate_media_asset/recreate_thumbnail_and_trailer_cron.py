from django.db.models import Q

from src.media.enums import MediaEnum
from src.media.models import Media
from src.storage.background_tasks.process_media_task.process_media_task import ProcessMediaTask
from src.storage.tasks import task_process_media


class RecreateThumbnailAndTrailerCron:
    def recreate_media_asset(self):
        media = (
            Media.objects
            .filter(file_type=MediaEnum.FILE_TYPE_VIDEO.value)
            .filter(Q(file_thumbnail__isnull=True) | Q(file_trailer__isnull=True))
        )

        for single_media in media:
            task_process_media.delay(
                media_id=single_media.id,
                media_type=ProcessMediaTask.MEDIA_TYPE_MEDIA,
                local_file_path=None,
                create_thumbnail=True if single_media.file_thumbnail is None else False,
                create_trailer=True if single_media.file_trailer is None else False,
                should_compress_media=False,
                download_from_remote=True,
            )
