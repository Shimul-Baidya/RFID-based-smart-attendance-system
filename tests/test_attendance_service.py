"""Unit tests for simulated RFID attendance business logic."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.attendance_service import (
    AttendanceSessionClosedError,
    DuplicateAttendanceError,
    RFIDCardNotFoundError,
    StudentNotEnrolledError,
    _validate_session_window,
)


def test_open_session_within_window_is_accepted() -> None:
    """Test that an open session within its window is accepted."""
    current_time = datetime.now(timezone.utc)
    session = {
        "status": "open",
        "attendance_opens_at": current_time - timedelta(minutes=5),
        "attendance_closes_at": current_time + timedelta(minutes=5),
    }

    _validate_session_window(session, current_time)


def test_closed_session_is_rejected() -> None:
    """Test that a closed session is rejected."""
    current_time = datetime.now(timezone.utc)
    session = {
        "status": "closed",
        "attendance_opens_at": current_time - timedelta(minutes=5),
        "attendance_closes_at": current_time + timedelta(minutes=5),
    }

    with pytest.raises(AttendanceSessionClosedError):
        _validate_session_window(session, current_time)


def test_scan_before_attendance_window_is_rejected() -> None:
    """Test that an early RFID scan is rejected."""
    current_time = datetime.now(timezone.utc)
    session = {
        "status": "open",
        "attendance_opens_at": current_time + timedelta(minutes=5),
        "attendance_closes_at": current_time + timedelta(minutes=10),
    }

    with pytest.raises(AttendanceSessionClosedError):
        _validate_session_window(session, current_time)


def test_service_exceptions_have_separate_meanings() -> None:
    """Test that feature failures use distinct exception classes."""
    assert RFIDCardNotFoundError is not StudentNotEnrolledError
    assert DuplicateAttendanceError is not AttendanceSessionClosedError
