"""Unit tests for the RFID attendance request schema."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.attendance_schema import (
    AttendanceScanRequest,
    AttendanceScanResponse,
)


def test_valid_scan_request() -> None:
    """
    Test the creation and normalization of a valid scan request.

    Returns:
        None.
    """
    request = AttendanceScanRequest(
        rfid_uid=" rfid-001 ",
        session_id=101,
    )

    assert request.rfid_uid == "RFID-001"
    assert request.session_id == 101


def test_empty_rfid_uid_is_rejected() -> None:
    """
    Test that an empty RFID UID raises a validation error.

    Returns:
        None.
    """
    with pytest.raises(ValidationError):
        AttendanceScanRequest(
            rfid_uid=" ",
            session_id=101,
        )


def test_invalid_session_id_is_rejected() -> None:
    """
    Test that a non-positive session ID raises a validation error.

    Returns:
        None.
    """
    with pytest.raises(ValidationError):
        AttendanceScanRequest(
            rfid_uid="RFID-001",
            session_id=0,
        )


def test_valid_scan_response() -> None:
    """
    Test the creation of a valid attendance scan response.

    Returns:
        None.
    """
    response = AttendanceScanResponse(
        message="Attendance recorded successfully",
        attendance_id=1,
        student_id=25,
        session_id=101,
        course_id=401,
        status="present",
        duplicate=False,
        recorded_at=datetime.now(timezone.utc),
    )

    assert response.course_id == 401
    assert response.status == "present"
    assert response.duplicate is False


def test_non_positive_course_id_is_rejected() -> None:
    """
    Test that a non-positive course ID is rejected.

        Returns:
            None.
    """
    with pytest.raises(ValidationError):
        AttendanceScanResponse(
            message="Attendance recorded successfully",
            attendance_id=1,
            student_id=25,
            session_id=101,
            course_id=0,
            status="present",
            duplicate=False,
            recorded_at=datetime.now(timezone.utc),
        )


def test_invalid_attendance_status_is_rejected() -> None:
    """
    Test that an unsupported attendance status is rejected.

    Returns:
        None.
    """
    with pytest.raises(ValidationError):
        AttendanceScanResponse(
            message="Attendance recorded successfully",
            attendance_id=1,
            student_id=25,
            session_id=101,
            course_id=401,
            status="unknown",  # type: ignore[arg-type]
            duplicate=False,
            recorded_at=datetime.now(timezone.utc),
        )
