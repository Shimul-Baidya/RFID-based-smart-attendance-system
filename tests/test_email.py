import pytest
from pydantic import ValidationError

from app.schemas.email_schema import AttendanceEmailData
from app.services.notification_service import EMAIL_TRIGGER_TYPES


class TestEmailTriggerTypes:
    """Tests for which notification types trigger an email."""

    def test_attendance_updated_triggers_email(self) -> None:
        assert "attendance_updated" in EMAIL_TRIGGER_TYPES

    def test_low_attendance_triggers_email(self) -> None:
        assert "low_attendance" in EMAIL_TRIGGER_TYPES

    def test_attendance_confirmed_does_not_trigger_email(self) -> None:
        assert "attendance_confirmed" not in EMAIL_TRIGGER_TYPES

class TestAttendanceEmailDataSchema:
    """Tests for the AttendanceEmailData schema."""

    def test_valid_email_data(self) -> None:
        data = AttendanceEmailData(
            student_name="Rahim Ahmed",
            student_email="rahim@example.com",
            course_name="CSE 403",
            class_date="30 August 2026",
            attendance_status="Absent",
        )

        assert data.student_name == "Rahim Ahmed"
        assert data.instructions is None

    def test_email_data_with_instructions(self) -> None:
        data = AttendanceEmailData(
            student_name="Karim Uddin",
            student_email="karim@example.com",
            course_name="STAT 305",
            class_date="30 August 2026",
            attendance_status="Low Attendance",
            instructions="Please attend upcoming classes regularly.",
        )

        assert data.instructions is not None

    def test_invalid_email_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AttendanceEmailData(
                student_name="Test",
                student_email="not-a-valid-email",
                course_name="CSE 403",
                class_date="30 August 2026",
                attendance_status="Absent",
            )

    def test_missing_required_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AttendanceEmailData(
                student_name="Test",
                student_email="test@example.com",
                course_name="CSE 403",
                attendance_status="Absent",
            )

class TestEmailTriggerTypes:
    """Tests for which notification types trigger an email."""

    def test_attendance_updated_triggers_email(self) -> None:
        assert "attendance_updated" in EMAIL_TRIGGER_TYPES

    def test_low_attendance_triggers_email(self) -> None:
        assert "low_attendance" in EMAIL_TRIGGER_TYPES

    def test_attendance_confirmed_does_not_trigger_email(self) -> None:
        assert "attendance_confirmed" not in EMAIL_TRIGGER_TYPES