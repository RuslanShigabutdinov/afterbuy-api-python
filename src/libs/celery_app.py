# import gevent
# import gevent.monkey
#
# gevent.monkey.patch_all()
import os
from celery import Celery

from src.config.redis import settings as redis_settings


celery_app: Celery = Celery(
    'afterbuy',
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=[
        'src.parser.tasks',
    ]
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)