import bugsnag
from celery import shared_task

from src.user.background_tasks.delete_user_media.delete_user_media_task import DeleteUserMediaTask


@shared_task
def task_delete_user_media(user_id: int):
    try:
        task = DeleteUserMediaTask()
        task.delete_user_media(user_id)
    except Exception as e:
        bugsnag.notify(e)
