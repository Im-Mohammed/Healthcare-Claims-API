from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=1800
)

# Optional: auto-discover tasks
celery_app.autodiscover_tasks(['app.Tasks'])
