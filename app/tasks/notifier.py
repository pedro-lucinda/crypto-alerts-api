# app/tasks/notifier.py

"""
Celery tasks for sending notifications when alerts fire.
"""

import requests
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.alert import Alert

# SQLAlchemy engine & session for standalone DB access in tasks
engine = create_engine(settings.sqlalchemy_database_uri)
SessionLocal = sessionmaker(bind=engine)


@shared_task(name="send_notification")
def send_notification(alert_id: int, price: float) -> None:
    """
    Send a notification for the given alert.

    - Loads the alert from the DB.
    - Calls the appropriate channel implementation.
    """
    db = SessionLocal()
    try:
        alert = db.query(Alert).get(alert_id)
        if not alert or not alert.is_active:
            return

        channel = alert.channel
        config = alert.channel_config  # JSONB

        payload = {
            "alert_id": alert.id,
            "symbol": alert.symbol,
            "threshold": str(alert.threshold),
            "direction": alert.direction,
            "price": price,
        }

        if channel == "webhook":
            url = config.get("url")
            if url:
                requests.post(url, json=payload, timeout=5.0)

        elif channel == "email":
            # TODO: integrate SendGrid here
            pass

        elif channel == "sms":
            # TODO: integrate Twilio here
            pass

        # Optionally, mark alert inactive or log history
    finally:
        db.close()
