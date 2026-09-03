"""
Manual script to verify the email service can send a real email
via Gmail SMTP. Run this once to confirm SMTP credentials work.

Usage: python -m tests.manual_check_email
"""

import asyncio

from app.schemas.email_schema import AttendanceEmailData
from app.services.email_service import send_attendance_email


async def main() -> None:
    test_data = AttendanceEmailData(
        student_name="Jemima",
        student_email="jemimarahman13@gmail.com",
        course_name="CSE 403",
        class_date="30 August 2026",
        attendance_status="Absent",
        instructions=(
            "If you believe this is incorrect, submit a correction "
            "request from your dashboard within 24 hours."
        ),
    )

    await send_attendance_email(test_data)
    print("Email sent successfully. Check the inbox.")


if __name__ == "__main__":
    asyncio.run(main())