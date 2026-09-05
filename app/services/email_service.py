"""Service for sending attendance-update emails via Gmail SMTP."""

import logging
import os
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv

from app.schemas.email_schema import AttendanceEmailData
from app.utils.notification_exceptions import NotificationDeliveryError

load_dotenv()

logger = logging.getLogger(__name__)


def _build_email_body(data: AttendanceEmailData) -> str:
    """Build the plain-text body for an attendance update email."""
    lines = [
        f"Dear {data.student_name},",
        "",
        f"Your attendance for {data.course_name} on {data.class_date} "
        f"was recorded as {data.attendance_status}.",
        "",
    ]

    if data.instructions:
        lines.append(data.instructions)
        lines.append("")

    lines.append("This is an automated message from the Attendance System.")

    return "\n".join(lines)


async def send_attendance_email(data: AttendanceEmailData) -> None:
    """Send an attendance-update email to a student via Gmail SMTP.

    Raises:
        NotificationDeliveryError: If the email could not be sent.
    """
    message = EmailMessage()
    message["From"] = os.environ["SMTP_FROM_EMAIL"]
    message["To"] = data.student_email
    message["Subject"] = f"Attendance update - {data.course_name}"
    message.set_content(_build_email_body(data))

    try:
        await aiosmtplib.send(
            message,
            hostname=os.environ["SMTP_HOST"],
            port=int(os.environ["SMTP_PORT"]),
            username=os.environ["SMTP_USERNAME"],
            password=os.environ["SMTP_PASSWORD"],
            start_tls=True,
        )
        logger.info(
            "Sent attendance email to %s for %s",
            data.student_email,
            data.course_name,
        )
    except Exception as exc:
        logger.error(
            "Failed to send attendance email to %s: %s",
            data.student_email,
            exc,
        )
        raise NotificationDeliveryError(
            f"Failed to send email to {data.student_email}"
        ) from exc

    