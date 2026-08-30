"""Define the database model for student attendance records."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AttendanceRecord(Base):
    """Represent one student's attendance result for one session.

    The model follows the shared ``attendance_records`` PostgreSQL
    table. A unique constraint on ``session_id`` and ``student_id``
    prevents the same student from receiving multiple attendance
    records for one session.

    Attributes:
        id: Unique attendance-record identifier.
        session_id: Identifier of the associated attendance session.
        student_id: Identifier of the student receiving attendance.
        rfid_card_id: Identifier of the RFID card used for the scan.
        status: Recorded attendance status.
        attendance_value: Numeric attendance value from zero to one.
        source: Method used to create the attendance record.
        scanned_at: Time at which the RFID card was scanned.
        recorded_at: Time at which the record was stored.
        modified_by: Identifier of the user who modified the record.
        modified_at: Time of the latest manual modification.
        correction_reason: Reason for manually correcting the record.
        teacher_remark: Optional remark provided by a teacher.
    """

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "student_id",
            name="uq_attendance_student_session",
        ),
        CheckConstraint(
            "status IN ('present', 'absent', 'late', 'fractional', 'excused')",
            name="ck_attendance_status",
        ),
        CheckConstraint(
            "attendance_value BETWEEN 0.00 AND 1.00",
            name="ck_attendance_value",
        ),
        CheckConstraint(
            "source IN ('rfid', 'manual', 'imported')",
            name="ck_attendance_source",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id"),
        nullable=False,
    )
    rfid_card_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("rfid_cards.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    attendance_value: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=Decimal("1.00"),
        server_default="1.00",
    )
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="rfid",
        server_default="rfid",
    )
    scanned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    modified_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    correction_reason: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )
    teacher_remark: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )
