from celery import Celery
from celery.signals import worker_init, worker_ready, worker_shutdown
from app.core.config import settings
from app.utils.logger import setup_celery_logging

# Setup logging for Celery worker
setup_celery_logging()

celery_app = Celery(
    "veritasad",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.video_analysis"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


@worker_init.connect
def init_worker(**kwargs):
    """Log worker initialization."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Celery worker initialized")


@worker_ready.connect
def worker_ready(**kwargs):
    """Log worker ready state."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Celery worker ready to accept tasks")


@worker_shutdown.connect
def shutdown_worker(**kwargs):
    """Log worker shutdown."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Celery worker shutting down")
