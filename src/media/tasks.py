import bugsnag
from celery import shared_task

from src.media.background_tasks.delete_media.delete_media_cron import DeleteMediaCron
from src.media.background_tasks.recreate_media_asset.recreate_thumbnail_and_trailer_cron import \
    RecreateThumbnailAndTrailerCron


@shared_task
def cron_recreate_thumbnail_and_trailer():
    try:
        task = RecreateThumbnailAndTrailerCron()
        task.recreate_media_asset()
    except Exception as e:
        bugsnag.notify(e)


@shared_task
def cron_delete_media():
    try:
        service = DeleteMediaCron()
        service.delete_media()
    except Exception as e:
        bugsnag.notify(e)
