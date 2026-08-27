import logging
from itertools import count

from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.utils.notification_exceptions import (
    DuplicateNotificationError,
)

logger = logging.getLogger(__name__)

# TODO(db-setup): remove this in-memory store once the real
# repository/database layer is available. This exists only so the
# service is runnable and testable before the DB is set up.
_notification_store: dict[int, dict] = {}
_id_counter = count(1)


async def create_attendance_notification(
    notification_data: NotificationCreate,
) -> NotificationResponse:
    """Create a confirmation notification for a successful RFID punch.

    Ensures only one notification is created per attendance record,
    so no duplicate notification is sent for the same class.
    """
    for existing in _notification_store.values():
        if existing["attendance_id"] == notification_data.attendance_id:
            raise DuplicateNotificationError(
                f"Notification already exists for attendance "
                f"{notification_data.attendance_id}"
            )

    new_id = next(_id_counter)
    record = {
        "id": new_id,
        "created_at": datetime_now(),
        **notification_data.model_dump(),
    }
    _notification_store[new_id] = record

    logger.info(
        "Created attendance notification %s for student %s",
        new_id,
        notification_data.student_id,
    )

    return NotificationResponse.model_validate(record)


async def get_student_notifications(
    student_id: int,
) -> list[NotificationResponse]:
    """Return all attendance notifications for a student's dashboard."""
    results = [
        NotificationResponse.model_validate(record)
        for record in _notification_store.values()
        if record["student_id"] == student_id
    ]
    return results


def datetime_now():
    """Small wrapper so it's easy to mock in tests later."""
    from datetime import datetime

    return datetime.utcnow()