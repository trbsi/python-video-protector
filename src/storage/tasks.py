import bugsnag
from celery import shared_task

from src.storage.background_tasks.clear_temp_folder.clear_temp_folder_cron import ClearTempFolderCron
from src.storage.background_tasks.process_media_task.process_media_task import ProcessMediaTask


@shared_task
def task_process_media(
        media_id: int,
        media_type: str,
        local_file_path: str | None,
        create_thumbnail: bool = False,
        create_trailer: bool = False,
        create_shards: bool = False,
        should_compress_media: bool = False,
        download_from_remote: bool = False,
) -> None:
    try:
        task = ProcessMediaTask()
        task.process_media(
            media_type=media_type,
            media_id=media_id,
            local_file_path=local_file_path,
            create_thumbnail=create_thumbnail,
            create_shards=create_shards,
            create_trailer=create_trailer,
            should_compress_media=should_compress_media,
            download_from_remote=download_from_remote
        )
    except Exception as e:
        bugsnag.notify(e)


@shared_task
def cron_clear_temp_folder():
    try:
        task = ClearTempFolderCron()
        task.clear_temp_folder()
    except Exception as e:
        bugsnag.notify(e)
