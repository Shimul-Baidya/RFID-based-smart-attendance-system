"""Unit tests for the RFID attendance request schema."""

import pytest
from pydantic import ValidationError

from app.schemas.attendance_schema import AttendanceScanRequest


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
