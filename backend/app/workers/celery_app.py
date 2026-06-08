from celery import Celery
from kombu import Queue

from app.config import settings

celery_app = Celery(
    "job_apply",
    broker=settings.redis_url,
    backend=settings.redis_url.replace("/0", "/1"),
    include=["app.workers.scrape_task"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_queues=(
        Queue("default"),
        Queue("scraping"),
    ),
    task_routes={
        "app.workers.scrape_task.run_scrape_pipeline": {"queue": "scraping"},
    },
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=settings.redis_url,
)
