"""
Manual script to verify create_and_notify sends an email and
updates email_status in the database correctly.

Usage: python -m tests.manual_check_email_trigger
"""

import asyncio

from app.database import AsyncSessionLocal
from app.schemas.email_schema import AttendanceEmailData
from app.schemas.notification_schema import NotificationCreate
from app.services.notification_service import create_and_notify


async def main() -> None:
    async with AsyncSessionLocal() as db:
        notification_data = NotificationCreate(
            user_id=1,
            attendance_record_id=None,
            notification_type="attendance_updated",
            title="Marked Absent",
            message="You were marked absent for CSE 403.",
            deduplication_key="manual-email-trigger-test-002",
        )

        email_data = AttendanceEmailData(
            student_name="Jemima",
            student_email="jemimarahman13@gmail.com",
            course_name="CSE 403",
            class_date="30 August 2026",
            attendance_status="Absent",
        )

        result = await create_and_notify(db, notification_data, email_data)
        print(f"Notification created with email_status: {result.email_status}")


if __name__ == "__main__":
    asyncio.run(main())