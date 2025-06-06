from celery import Celery, signals

from app.core import config
from app.task import multiply
from app.cron_jobs.invoice import check_active_sub_and_generate_invoice
from celery.schedules import crontab



print(f"result backend --> {config.settings.CELERY_RESULT_BACKEND}")
print(f"broker_url --> {config.settings.CELERY_BROKER_URL}")

# Create a Celery application
celery_app = Celery(
    __name__,
    broker=config.settings.CELERY_BROKER_URL,
    backend=config.settings.CELERY_RESULT_BACKEND,
)


@signals.task_postrun.connect
def task_post_run_signal_handler(task_id, task, args, kwargs, retval, state, **extra):
    print(f"Task {task_id} completed with result: {retval}")

    print(f"task ----> {task}")
    print(f"arguments : --> {args}")
    print(f"extra --> {extra}")
    print(f"retry ---> {retval}")
    print(f"state --> {state}")


@signals.task_prerun.connect
def task_pre_run_signal_handler(task_id, task, args, kwargs, **extra):
    """
    This signal is used and executed
    before task is executed
    :param task_id: task_id
    :param task: task_name
    :param args: arguments passed
    :param kwargs: key word argument passed
    :return: None
    """
    print(f"Task {task_id} started ")
    print(f"task_name  in the pre-signals --> {task}")
    print(f"arguments ins the pre-signals --> {args}")
    print(f"extra key words --> {extra}")


# Generate the invoice for active subscriptions
celery_app.conf.beat_schedule = {
    "create-event-on-missing-time": {
        "task": "app.cron_jobs.invoice.check_active_sub_and_generate_invoice",
        "schedule": crontab(minute="*/1"),  # Runs every minute
    },
}
celery_app.conf.timezone = "Asia/Kolkata"
