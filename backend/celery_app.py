from celery import Celery

from .settings import get_settings

settings = get_settings()

celery_app = Celery(
    "veritasad",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {"backend.tasks.*": {"queue": "veritasad"}}
celery_app.conf.update(task_track_started=True, task_serializer="json", result_serializer="json")
celery_app.autodiscover_tasks(["backend"])

