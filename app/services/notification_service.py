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

    Uses `deduplication_key` to ensure only one notification is
    created per attendance event, matching the unique constraint
    on the shared `notifications` table.
    """
    if notification_data.deduplication_key is not None:
        for existing in _notification_store.values():
            if (
                existing["deduplication_key"]
                == notification_data.deduplication_key
            ):
                raise DuplicateNotificationError(
                    "A notification with this deduplication key "
                    "already exists"
                )

    new_id = next(_id_counter)
    record = {
        "id": new_id,
        "is_read": False,
        "email_status": "not_requested",
        "created_at": _now(),
        "read_at": None,
        **notification_data.model_dump(),
    }
    _notification_store[new_id] = record

    logger.info(
        "Created notification %s for user %s",
        new_id,
        notification_data.user_id,
    )

    return NotificationResponse.model_validate(record)


async def get_user_notifications(
    user_id: int,
) -> list[NotificationResponse]:
    """Return all notifications for a user's dashboard."""
    results = [
        NotificationResponse.model_validate(record)
        for record in _notification_store.values()
        if record["user_id"] == user_id
    ]
    return results


def _now():
    """Small wrapper so it's easy to mock in tests later."""
    from datetime import datetime

    return datetime.utcnow()