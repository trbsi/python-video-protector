import bugsnag
from celery import shared_task

from src.payment.services.payout.payout_service import PayoutService


@shared_task
def cron_payout_creator():
    try:
        task_payout_creator.delay()
    except Exception as e:
        bugsnag.notify(e)


@shared_task
def task_payout_creator():
    try:
        service = PayoutService()
        service.do_payout()
    except Exception as e:
        bugsnag.notify(e)
