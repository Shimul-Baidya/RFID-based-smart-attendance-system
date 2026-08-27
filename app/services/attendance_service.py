"""Provide business logic for simulated RFID attendance scans."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.attendance_model import AttendanceRecord
from app.schemas.attendance_schema import AttendanceScanResponse


class AttendanceServiceError(Exception):
    """Base exception for attendance-service failures."""


class RFIDCardNotFoundError(AttendanceServiceError):
    """Indicate that no active student and RFID card were found."""


class AttendanceSessionNotFoundError(AttendanceServiceError):
    """Indicate that the requested attendance session was not found."""


class AttendanceSessionClosedError(AttendanceServiceError):
    """Indicate that the session is not accepting attendance scans."""


class StudentNotEnrolledError(AttendanceServiceError):
    """Indicate that the student is not actively enrolled."""


class DuplicateAttendanceError(AttendanceServiceError):
    """Indicate that attendance already exists for the session."""


def mark_attendance(
    database: Session,
    rfid_uid: str,
    session_id: int,
) -> AttendanceScanResponse:
    """Record attendance from a simulated RFID scan.

    Args:
        database: Active SQLAlchemy database session.
        rfid_uid: Normalized RFID-card identifier.
        session_id: Identifier of the requested attendance session.

    Returns:
        A validated response describing the created attendance record.

    Raises:
        RFIDCardNotFoundError: If the card or student is not active.
        AttendanceSessionNotFoundError: If the session does not exist.
        AttendanceSessionClosedError: If attendance is not currently open.
        StudentNotEnrolledError: If the student is not actively enrolled.
        DuplicateAttendanceError: If attendance already exists.
    """
    current_time = datetime.now(timezone.utc)
    card = _find_active_card(database, rfid_uid)

    if card is None:
        raise RFIDCardNotFoundError("No active student was found for this RFID card.")

    session = _find_session(database, session_id)

    if session is None:
        raise AttendanceSessionNotFoundError("The attendance session was not found.")

    _validate_session_window(session, current_time)

    if not _is_actively_enrolled(
        database,
        offering_id=session["offering_id"],
        student_id=card["student_id"],
    ):
        raise StudentNotEnrolledError(
            "The student is not actively enrolled in this course offering."
        )

    if _attendance_exists(
        database,
        session_id=session_id,
        student_id=card["student_id"],
    ):
        raise DuplicateAttendanceError(
            "Attendance has already been recorded for this session."
        )

    record = AttendanceRecord(
        session_id=session_id,
        student_id=card["student_id"],
        rfid_card_id=card["rfid_card_id"],
        status="present",
        attendance_value=1.0,
        source="rfid",
        scanned_at=current_time,
        recorded_at=current_time,
    )

    try:
        database.add(record)
        database.commit()
        database.refresh(record)
    except IntegrityError as error:
        database.rollback()
        raise DuplicateAttendanceError(
            "Attendance has already been recorded for this session."
        ) from error

    return AttendanceScanResponse(
        message="Attendance recorded successfully",
        attendance_id=record.id,
        student_id=record.student_id,
        session_id=record.session_id,
        course_id=session["course_id"],
        status=record.status,
        duplicate=False,
        recorded_at=record.recorded_at,
    )


def _find_active_card(
    database: Session,
    rfid_uid: str,
) -> dict[str, Any] | None:
    """Return the active RFID card and its active student."""
    query = text(
        """
        SELECT
            rfid_cards.id AS rfid_card_id,
            rfid_cards.student_id AS student_id
        FROM rfid_cards
        JOIN students
            ON students.id = rfid_cards.student_id
        WHERE UPPER(BTRIM(rfid_cards.uid)) = :rfid_uid
          AND rfid_cards.status = 'active'
          AND students.status = 'active'
        """
    )

    result = (
        database.execute(
            query,
            {"rfid_uid": rfid_uid},
        )
        .mappings()
        .one_or_none()
    )

    return dict(result) if result is not None else None


def _find_session(
    database: Session,
    session_id: int,
) -> dict[str, Any] | None:
    """Return an attendance session and its associated course."""
    query = text(
        """
        SELECT
            attendance_sessions.id,
            attendance_sessions.offering_id,
            attendance_sessions.status,
            attendance_sessions.attendance_opens_at,
            attendance_sessions.attendance_closes_at,
            course_offerings.course_id
        FROM attendance_sessions
        JOIN course_offerings
            ON course_offerings.id = attendance_sessions.offering_id
        WHERE attendance_sessions.id = :session_id
        """
    )

    result = (
        database.execute(
            query,
            {"session_id": session_id},
        )
        .mappings()
        .one_or_none()
    )

    return dict(result) if result is not None else None


def _validate_session_window(
    session: dict[str, Any],
    current_time: datetime,
) -> None:
    """Validate that a session currently accepts attendance."""
    is_open = session["status"] == "open"
    is_within_window = (
        session["attendance_opens_at"]
        <= current_time
        <= session["attendance_closes_at"]
    )

    if not is_open or not is_within_window:
        raise AttendanceSessionClosedError(
            "The attendance session is not currently open."
        )


def _is_actively_enrolled(
    database: Session,
    offering_id: int,
    student_id: int,
) -> bool:
    """Return whether a student has an active enrollment."""
    query = text(
        """
        SELECT id
        FROM enrollments
        WHERE offering_id = :offering_id
          AND student_id = :student_id
          AND status = 'active'
        """
    )

    enrollment_id = database.execute(
        query,
        {
            "offering_id": offering_id,
            "student_id": student_id,
        },
    ).scalar_one_or_none()

    return enrollment_id is not None


def _attendance_exists(
    database: Session,
    session_id: int,
    student_id: int,
) -> bool:
    """Return whether attendance already exists."""
    query = text(
        """
        SELECT id
        FROM attendance_records
        WHERE session_id = :session_id
          AND student_id = :student_id
        """
    )

    attendance_id = database.execute(
        query,
        {
            "session_id": session_id,
            "student_id": student_id,
        },
    ).scalar_one_or_none()

    return attendance_id is not None
