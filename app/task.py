from celery import shared_task


@shared_task
def process_task():
    # Task logic goes here
    addition = 10 + 20
    return addition


@shared_task
def multiply():
    mul = 10 * 20
    return mul
