"""Service for creating attendance notifications and triggering emails."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_model import Notification
from app.schemas.email_schema import AttendanceEmailData
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.email_service import send_attendance_email
from app.utils.notification_exceptions import (
    DuplicateNotificationError,
    NotificationDeliveryError,
)

logger = logging.getLogger(__name__)

EMAIL_TRIGGER_TYPES = {"attendance_updated", "low_attendance"}


async def create_attendance_notification(
    db: AsyncSession,
    notification_data: NotificationCreate,
) -> NotificationResponse:
    """Create a confirmation notification for a successful RFID punch.

    Uses `deduplication_key` to ensure only one notification is
    created per attendance event, matching the unique constraint
    on the shared `notifications` table.
    """
    if notification_data.deduplication_key is not None:
        result = await db.execute(
            select(Notification).where(
                Notification.deduplication_key
                == notification_data.deduplication_key
            )
        )
        existing = result.scalar_one_or_none()

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
    await db.commit()
    await db.refresh(notification)

    logger.info(
        "Created notification %s for user %s",
        notification.id,
        notification.user_id,
    )

    return NotificationResponse.model_validate(notification)


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
) -> list[NotificationResponse]:
    """Return all notifications for a user's dashboard."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return [
        NotificationResponse.model_validate(n) for n in notifications
    ]


async def create_and_notify(
    db: AsyncSession,
    notification_data: NotificationCreate,
    email_data: AttendanceEmailData | None = None,
) -> NotificationResponse:
    """Create a notification and send an email if the type requires it.

    Only 'attendance_updated' (used for absent marks) and
    'low_attendance' notification types trigger an email, per SRS 3.1.7.
    If email sending fails, the in-app notification is still kept
    and visible on the dashboard; email_status is updated to reflect
    delivery outcome.
    """
    notification = await create_attendance_notification(
        db, notification_data
    )

    should_email = (
        notification_data.notification_type in EMAIL_TRIGGER_TYPES
        and email_data is not None
    )

    if should_email:
        result = await db.execute(
            select(Notification).where(Notification.id == notification.id)
        )
        db_notification = result.scalar_one()
        db_notification.email_status = "pending"
        await db.commit()

        try:
            await send_attendance_email(email_data)
            db_notification.email_status = "sent"
        except NotificationDeliveryError:
            logger.warning(
                "Email failed for notification %s, dashboard "
                "notification remains visible",
                notification.id,
            )
            db_notification.email_status = "failed"

        await db.commit()
        await db.refresh(db_notification)
        notification = NotificationResponse.model_validate(db_notification)

    return notification
