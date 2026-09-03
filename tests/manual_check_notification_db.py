"""
Manual script to verify the notification service can write to
and read from the real PostgreSQL database. Run this once to
confirm the DB connection and service layer work end-to-end.

Usage: python tests/manual_check_notification_db.py
"""

import asyncio

from app.database import AsyncSessionLocal
from app.schemas.notification_schema import NotificationCreate
from app.services.notification_service import (
    create_attendance_notification,
    get_user_notifications,
)


async def main() -> None:
    async with AsyncSessionLocal() as db:
        notification_data = NotificationCreate(
            user_id=1,
            attendance_record_id=None,
            notification_type="attendance_confirmed",
            title="Test Notification",
            message="This is a manual test notification.",
            deduplication_key="manual-test-key-001",
        )

        created = await create_attendance_notification(
            db, notification_data
        )
        print(f"Created notification: {created}")

        notifications = await get_user_notifications(db, user_id=1)
        print(f"Notifications for user 1: {notifications}")


if __name__ == "__main__":
    asyncio.run(main())