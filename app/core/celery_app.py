# app/core/celery_app.py

"""
Celery application factory and configuration.
Explicitly imports task modules so they’re always registered.
"""

from celery import Celery
from celery.schedules import crontab

import app.tasks.notifier  # pylint: disable=unused-import
import app.tasks.poller  # pylint: disable=unused-import
from app.core.config import settings

# Instantiate the Celery app
celery_app = Celery(
    "crypto_alerts",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


# Beat schedule: run poll_all_symbols every minute
celery_app.conf.beat_schedule = {
    "poll-all-symbols-every-minute": {
        "task": "poll_all_symbols",
        "schedule": crontab(minute="*"),
    },
}
