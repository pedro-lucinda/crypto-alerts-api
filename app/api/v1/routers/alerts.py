from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, get_db_session
from app.models.alert import Alert as AlertModel
from app.models.user import User as UserModel
from app.schemas.alert import AlertCreate, AlertRead, AlertUpdate

router = APIRouter(tags=["alerts"])


@router.post(
    "",
    response_model=AlertRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new price alert",
    description="Register a new price alert for the authenticated user.",
)
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create and persist a new Alert.

    - **symbol**: Trading pair symbol, e.g. 'BTCUSDT'
    - **threshold**: Price at which to trigger
    - **direction**: 'above' or 'below'
    - **channel**: Notification channel
    - **channel_config**: Channel-specific settings
    """
    alert = AlertModel(
        user_id=current_user.id,
        symbol=alert_in.symbol,
        threshold=alert_in.threshold,
        direction=alert_in.direction,
        channel=alert_in.channel,
        channel_config=alert_in.channel_config,
        is_active=alert_in.is_active,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get(
    "",
    response_model=List[AlertRead],
    summary="List all price alerts",
    description="Retrieve all active and inactive alerts belonging to the "
    "authenticated user.",
)
def read_alerts(
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    List all alerts for the current user.
    """
    alerts = db.query(AlertModel).filter(AlertModel.user_id == current_user.id).all()
    return alerts


@router.get(
    "/{alert_id}",
    response_model=AlertRead,
    summary="Get a single alert",
    description="Retrieve a specific alert by its ID for the authenticated user.",
)
def read_alert(
    alert_id: int,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Fetch one Alert by ID if it belongs to the current user.
    """
    alert = (
        db.query(AlertModel)
        .filter(AlertModel.id == alert_id, AlertModel.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )
    return alert


@router.put(
    "/{alert_id}",
    response_model=AlertRead,
    summary="Update an existing alert",
    description="Modify threshold, channel settings, or activation status of an existing alert.",
)
def update_alert(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update fields of an existing Alert. Only provided fields will be changed.
    """
    alert = (
        db.query(AlertModel)
        .filter(AlertModel.id == alert_id, AlertModel.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )

    update_data = alert_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    db.commit()
    db.refresh(alert)
    return alert


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an alert",
    description="Remove an alert by ID for the authenticated user.",
)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Permanently delete an Alert.
    """
    alert = (
        db.query(AlertModel)
        .filter(AlertModel.id == alert_id, AlertModel.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )

    db.delete(alert)
    db.commit()
    return None
