from celery import Celery


celery_app = Celery(
    "time_table_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.autodiscover_tasks(['app.tasks_folder'])

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Tehran',
    enable_utc=True,
    task_soft_time_limit=180, # After 180s if the task had not finished and exception would happen.
    task_ack_late=True,
    worker_concurrency=2, # Each worker can run x tasks together.
    worker_prefetch_multiplier=1 # Length of worker's queue.
)
