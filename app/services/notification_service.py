import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_model import Notification
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.utils.notification_exceptions import (
    DuplicateNotificationError,
)

logger = logging.getLogger(__name__)


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