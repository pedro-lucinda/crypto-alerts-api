# app/tasks/poller.py

"""
Celery tasks for polling crypto prices from Binance,
caching them in Redis, and enqueuing notifications when
alerts are triggered.
"""

from decimal import Decimal
from typing import Optional

import httpx
import redis
from celery import group, shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.alert import Alert
from app.tasks.notifier import send_notification

# Redis client for caching prices
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# SQLAlchemy engine & session for standalone DB access in tasks
engine = create_engine(settings.sqlalchemy_database_uri)
SessionLocal = sessionmaker(bind=engine)


@shared_task(
    name="poll_price",
    bind=True,
    autoretry_for=(httpx.RequestError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def poll_price(self, symbol: str) -> Optional[float]:
    """
    Fetch the latest price for a given symbol from Binance,
    cache it in Redis, then check and enqueue notifications
    for any alerts that have their threshold crossed.

    - On HTTP 400 (bad symbol), we log & return None without retry.
    - On other HTTP/network errors, retry up to 3 times.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        price = float(Decimal(data["price"]))

        # Cache in Redis for 120 seconds
        key = f"price:{symbol.upper()}"
        redis_client.set(key, price, ex=120)

        # Check active alerts and enqueue notifications
        db = SessionLocal()
        try:
            alerts = (
                db.query(Alert)
                .filter(Alert.symbol == symbol.upper(), Alert.is_active.is_(True))
                .all()
            )
            for alert in alerts:
                threshold = float(alert.threshold)
                if (alert.direction == "above" and price >= threshold) or (
                    alert.direction == "below" and price <= threshold
                ):
                    send_notification.delay(alert.id, price)
        finally:
            db.close()

        return price

    except httpx.HTTPStatusError as e:
        # 400 Bad Request means the symbol is invalid—log & stop
        if e.response.status_code == 400:
            # you could log symbol here if you have a logger
            print(f"poll_price: invalid symbol '{symbol}' → skipping")
            return None
        # for other HTTP status codes, retry
        raise self.retry(exc=e)

    except httpx.RequestError as e:
        # network / timeout issues
        raise self.retry(exc=e)

    except Exception as e:
        # anything else: retry
        raise self.retry(exc=e)


@shared_task(name="poll_all_symbols")
def poll_all_symbols() -> None:
    """
    Fetch all distinct, active alert symbols from the database
    (as plain strings) and dispatch individual poll_price tasks in parallel.
    """
    db = SessionLocal()
    try:
        # Query for distinct symbols; .all() returns list of one‐item tuples
        rows = db.query(Alert.symbol).filter(Alert.is_active.is_(True)).distinct().all()
        symbols = [row[0] for row in rows]

        if symbols:
            job = group(poll_price.s(sym) for sym in symbols)
            job.apply_async()
    finally:
        db.close()
