from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


NotificationType = Literal[
    "attendance_confirmed",
    "attendance_updated",
    "attendance_rejected",
    "low_attendance",
    "correction_submitted",
    "correction_decided",
    "session_opened",
    "report_ready",
]


class NotificationCreate(BaseModel):
    user_id: int
    attendance_record_id: int | None = None
    notification_type: NotificationType
    title: str
    message: str
    deduplication_key: str | None = None


class NotificationResponse(BaseModel):
    id: int
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    email_status: str
    created_at: datetime
    read_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)