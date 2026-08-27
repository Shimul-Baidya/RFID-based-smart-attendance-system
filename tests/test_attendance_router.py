"""Unit tests for the RFID attendance API endpoint."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.routers import attendance_router
from app.schemas.attendance_schema import AttendanceScanResponse
from app.services.attendance_service import (
    AttendanceSessionClosedError,
    AttendanceSessionNotFoundError,
    DuplicateAttendanceError,
    RFIDCardNotFoundError,
    StudentNotEnrolledError,
)


@pytest.fixture
def database() -> MagicMock:
    """Provide a mocked SQLAlchemy database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client(database: MagicMock) -> TestClient:
    """Provide a test client with a mocked database dependency."""
    application = FastAPI()
    application.include_router(attendance_router.router)

    def override_database() -> MagicMock:
        """Return the mocked database session."""
        return database

    application.dependency_overrides[get_database] = override_database

    return TestClient(application)


def test_successful_attendance_scan_returns_created(
    client: TestClient,
    database: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a successful simulated RFID attendance scan."""
    expected_response = AttendanceScanResponse(
        message="Attendance recorded successfully",
        attendance_id=1,
        student_id=25,
        session_id=101,
        course_id=401,
        status="present",
        duplicate=False,
        recorded_at=datetime.now(timezone.utc),
    )

    def successful_scan(
        database: Session,
        rfid_uid: str,
        session_id: int,
    ) -> AttendanceScanResponse:
        """Return a successful attendance response."""
        assert database is not None
        assert rfid_uid == "RFID-001"
        assert session_id == 101
        return expected_response

    monkeypatch.setattr(
        attendance_router,
        "mark_attendance",
        successful_scan,
    )

    response = client.post(
        "/attendance/scan",
        json={
            "rfid_uid": " rfid-001 ",
            "session_id": 101,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["attendance_id"] == 1
    assert response.json()["status"] == "present"
    assert response.json()["duplicate"] is False


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (
            RFIDCardNotFoundError("RFID card not found."),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            AttendanceSessionNotFoundError("Session not found."),
            status.HTTP_404_NOT_FOUND,
        ),
        (
            AttendanceSessionClosedError("Session is closed."),
            status.HTTP_409_CONFLICT,
        ),
        (
            StudentNotEnrolledError("Student is not enrolled."),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            DuplicateAttendanceError("Attendance already exists."),
            status.HTTP_409_CONFLICT,
        ),
    ],
)
def test_service_errors_are_mapped_to_http_responses(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    service_error: Exception,
    expected_status: int,
) -> None:
    """Test that service failures receive meaningful HTTP statuses."""

    def failed_scan(
        database: Session,
        rfid_uid: str,
        session_id: int,
    ) -> AttendanceScanResponse:
        """Raise the configured service exception."""
        del database, rfid_uid, session_id
        raise service_error

    monkeypatch.setattr(
        attendance_router,
        "mark_attendance",
        failed_scan,
    )

    response = client.post(
        "/attendance/scan",
        json={
            "rfid_uid": "RFID-001",
            "session_id": 101,
        },
    )

    assert response.status_code == expected_status
    assert response.json()["detail"] == str(service_error)


def test_invalid_scan_request_returns_unprocessable_entity(
    client: TestClient,
) -> None:
    """Test FastAPI validation for an invalid scan request."""
    response = client.post(
        "/attendance/scan",
        json={
            "rfid_uid": " ",
            "session_id": 0,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
