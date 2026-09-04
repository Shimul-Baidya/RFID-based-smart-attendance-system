"""Unit tests for the attendance database model."""

from decimal import Decimal

from app.models.attendance_model import AttendanceRecord


def test_attendance_record_table_name() -> None:
    """Test that the model uses the shared attendance table name."""
    assert AttendanceRecord.__tablename__ == "attendance_records"


def test_attendance_record_contains_required_columns() -> None:
    """Test that the model contains the shared database fields."""
    expected_columns = {
        "id",
        "session_id",
        "student_id",
        "rfid_card_id",
        "status",
        "attendance_value",
        "source",
        "scanned_at",
        "recorded_at",
        "modified_by",
        "modified_at",
        "correction_reason",
        "teacher_remark",
    }

    assert set(AttendanceRecord.__table__.columns.keys()) == expected_columns


def test_attendance_record_uses_rfid_defaults() -> None:
    """Test the default values used for a simulated RFID scan."""
    record = AttendanceRecord(
        session_id=101,
        student_id=25,
        status="present",
    )

    assert record.attendance_value is None
    assert record.source is None

    attendance_default = AttendanceRecord.__table__.columns.attendance_value.default
    source_default = AttendanceRecord.__table__.columns.source.default

    assert attendance_default is not None
    assert attendance_default.arg == Decimal("1.00")
    assert source_default is not None
    assert source_default.arg == "rfid"


def test_student_session_unique_constraint_exists() -> None:
    """Test that duplicate attendance has a database constraint."""
    constraint_names = {
        constraint.name for constraint in AttendanceRecord.__table__.constraints
    }

    assert "uq_attendance_student_session" in constraint_names
