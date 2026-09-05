"""Service for creating and retrieving attendance notifications."""

import logging

from sqlalchemy.orm import Session

from app.models.notification_model import Notification
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.utils.notification_exceptions import DuplicateNotificationError

logger = logging.getLogger(__name__)


def create_attendance_notification(
    db: Session,
    notification_data: NotificationCreate,
) -> NotificationResponse:
    """Create a confirmation notification for a successful RFID punch."""
    if notification_data.deduplication_key is not None:
        existing = (
            db.query(Notification)
            .filter(
                Notification.deduplication_key
                == notification_data.deduplication_key
            )
            .first()
        )

        if existing is not None:
            raise DuplicateNotificationError(
                "A notification with this deduplication key "
                "already exists"
            )

    notification = Notification(
        user_id=notification_data.user_id,
        attendance_record_id=notification_data.attendance_record_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        deduplication_key=notification_data.deduplication_key,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    logger.info(
        "Created notification %s for user %s",
        notification.id,
        notification.user_id,
    )

    return NotificationResponse.model_validate(notification)


def get_user_notifications(
    db: Session,
    user_id: int,
) -> list[NotificationResponse]:
    """Return all notifications for a user's dashboard."""
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        NotificationResponse.model_validate(n) for n in notifications
    ]