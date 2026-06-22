from celery import Celery
from core.config import settings

celery_app = Celery(
    "rafflix_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-active-raffles-every-minute": {
            "task": "worker.tasks.check_raffles",
            "schedule": 60.0,
        },
    }
)
