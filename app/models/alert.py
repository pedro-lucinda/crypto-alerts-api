# app/models/alert.py

"""
SQLAlchemy model for price alerts.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from sqlalchemy.sql import expression

from app.db.base import Base


class Alert(Base):
    """
    Represents a user-defined price alert.

    Attributes:
        id:            Unique identifier.
        user_id:       FK to the owning User.
        symbol:        Trading pair symbol (e.g. 'BTCUSDT').
        threshold:     Price at which the alert fires.
        direction:     'above' or 'below' behavior.
        channel:       Notification channel.
        channel_config:JSON blob for channel settings.
        is_active:     Whether the alert is live.
        created_at:    Timestamp when created (UTC).
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(Text, nullable=False, index=True)
    threshold = Column(Numeric, nullable=False)
    direction = Column(
        Text,
        nullable=False,
        doc="Trigger when price goes 'above' or 'below' threshold",
    )
    channel = Column(
        Text,
        nullable=False,
        doc="Notification channel: 'email', 'sms' or 'webhook'",
    )
    channel_config = Column(
        JSON,
        nullable=False,
        doc="Channel-specific settings, e.g. {'email':'user@…'} or {'url':'https://…'}",
    )
    is_active = Column(
        Boolean,
        nullable=False,
        server_default=expression.true(),
        doc="True if the alert is enabled",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
        doc="UTC timestamp when the alert was created",
    )
