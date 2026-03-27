try:
    from celery import Celery
    from kombu import Queue
    from celery.signals import worker_init, worker_ready, worker_shutdown
except ImportError:  # pragma: no cover - optional dependency for worker runtime
    Celery = None  # type: ignore[assignment]

    class _Signal:
        def connect(self, func):
            return func

    worker_init = _Signal()
    worker_ready = _Signal()
    worker_shutdown = _Signal()

from app.core.config import settings
from app.utils.logger import setup_celery_logging

# Setup logging for Celery worker
setup_celery_logging()


class _DummyCeleryApp:
    def task(self, *args, **kwargs):
        def decorator(func):
            def delay(*delay_args, **delay_kwargs):
                return func(None, *delay_args, **delay_kwargs)

            func.delay = delay  # type: ignore[attr-defined]
            func.apply_async = lambda args=None, kwargs=None, **_options: func(  # type: ignore[attr-defined]
                None,
                *(args or ()),
                **(kwargs or {}),
            )
            return func

        return decorator

    class conf:
        @staticmethod
        def update(*args, **kwargs):
            return None


if Celery is None:
    celery_app = _DummyCeleryApp()
else:
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
        task_default_queue="analysis",
        task_default_exchange="analysis",
        task_default_routing_key="analysis",
        task_queues=(
            Queue("analysis", routing_key="analysis"),
            Queue("download", routing_key="download"),
        ),
        task_routes={
            "analyze_video": {"queue": "analysis", "routing_key": "analysis"},
            "download_video": {"queue": "download", "routing_key": "download"},
        },
        task_track_started=settings.CELERY_TASK_TRACK_STARTED,
        task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
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
