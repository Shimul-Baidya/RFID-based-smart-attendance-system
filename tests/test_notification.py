from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.utils.notification_exceptions import (
    DuplicateNotificationError,
    NotificationDeliveryError,
    NotificationError,
)


class TestNotificationCreateSchema:
    """Tests for the NotificationCreate request schema."""

    def test_valid_notification_create(self) -> None:
        notification = NotificationCreate(
            user_id=1,
            attendance_record_id=10,
            notification_type="attendance_confirmed",
            title="Attendance Confirmed",
            message="Your attendance for CSE 403 was recorded as Present.",
            deduplication_key="session-10-user-1",
        )

        assert notification.user_id == 1
        assert notification.notification_type == "attendance_confirmed"

    def test_notification_create_without_optional_fields(self) -> None:
        notification = NotificationCreate(
            user_id=2,
            notification_type="low_attendance",
            title="Low Attendance Warning",
            message="Your attendance has fallen below 75%.",
        )

        assert notification.attendance_record_id is None
        assert notification.deduplication_key is None

    def test_invalid_notification_type_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NotificationCreate(
                user_id=1,
                notification_type="not_a_real_type",
                title="Invalid",
                message="This should fail.",
            )

    def test_missing_required_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NotificationCreate(
                user_id=1,
                notification_type="attendance_confirmed",
                message="Missing title field.",
            )


class TestNotificationResponseSchema:
    """Tests for the NotificationResponse schema."""

    def test_valid_notification_response(self) -> None:
        response = NotificationResponse(
            id=1,
            notification_type="attendance_confirmed",
            title="Attendance Confirmed",
            message="Recorded as Present.",
            is_read=False,
            email_status="not_requested",
            created_at=datetime.utcnow(),
            read_at=None,
        )

        assert response.is_read is False
        assert response.read_at is None

    def test_notification_response_with_read_receipt(self) -> None:
        now = datetime.utcnow()
        response = NotificationResponse(
            id=2,
            notification_type="attendance_confirmed",
            title="Attendance Confirmed",
            message="Recorded as Present.",
            is_read=True,
            email_status="sent",
            created_at=now,
            read_at=now,
        )

        assert response.is_read is True
        assert response.read_at is not None


class TestNotificationExceptions:
    """Tests for custom notification exceptions."""

    def test_duplicate_notification_error_is_notification_error(self) -> None:
        assert issubclass(DuplicateNotificationError, NotificationError)

    def test_delivery_error_is_notification_error(self) -> None:
        assert issubclass(NotificationDeliveryError, NotificationError)

    def test_duplicate_notification_error_message(self) -> None:
        with pytest.raises(DuplicateNotificationError, match="already exists"):
            raise DuplicateNotificationError(
                "A notification with this deduplication key already exists"
            )

    def test_notification_error_can_be_caught_as_exception(self) -> None:
        with pytest.raises(Exception):
            raise NotificationError("Generic notification failure")