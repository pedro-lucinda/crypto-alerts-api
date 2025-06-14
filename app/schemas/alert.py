"""
Pydantic schemas for alert operations.
"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    """
    Shared properties for all alerts operations.
    """

    symbol: str = Field(..., description="Trading pair symbol, e.g. 'BTCUSDT'")
    threshold: float = Field(..., description="Price threshold that triggers the alert")
    direction: Literal["above", "below"] = Field(
        ...,
        description="Whether to trigger when price goes above or below the threshold",
    )
    channel: Literal["email", "sms", "webhook"] = Field(
        ..., description="Notification channel"
    )
    channel_config: Any = Field(
        ...,
        description="Channel-specific configuration (e.g., email address or webhook URL)",
    )
    is_active: Optional[bool] = Field(
        True, description="Whether this alert is currently active"
    )


class AlertCreate(AlertBase):
    """
    Properties required to create a new alert.
    """

    pass


class AlertRead(AlertBase):
    """
    Properties returned when reading an alert.
    """

    id: int = Field(..., description="Unique identifier of the alert")
    user_id: int = Field(..., description="ID of the user who owns this alert")
    created_at: datetime = Field(
        ..., description="Timestamp when the alert was created"
    )

    class Config:
        """
        Pydantic configuration to enable ORM mode.
        Allows reading data from ORM models.
        """

        from_attributes = True


class AlertUpdate(BaseModel):
    """
    Fields for updating an existing alert.
    Only the provided (non-null) fields will be applied.
    """

    symbol: Optional[str] = Field(
        None, description="Trading pair symbol, e.g. 'BTCUSDT'"
    )
    threshold: Optional[float] = Field(
        None, description="Price threshold that triggers the alert"
    )
    direction: Optional[Literal["above", "below"]] = Field(
        None,
        description="Whether to trigger when price goes above or below the threshold",
    )
    channel: Optional[Literal["email", "sms", "webhook"]] = Field(
        None, description="Notification channel"
    )
    channel_config: Optional[Any] = Field(
        None,
        description="Channel-specific configuration (e.g., email address or webhook URL)",
    )
    is_active: Optional[bool] = Field(
        None, description="Set to false to deactivate the alert"
    )

    class Config:
        """
        Allow population by ORM objects; ignore extra fields.
        """

        from_attributes = True
