"""Repository implementations used by attendance report generation."""

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.report_schema import AttendanceReportFilters


@dataclass(frozen=True, slots=True)
class AttendanceReportRow:
    """Latest effective attendance record returned by the data layer."""

    student_id: int
    student_number: str
    student_name: str
    status: str
    attendance_value: float
    recorded_at: datetime
    modified_at: datetime | None = None
    department: str = ""
    batch: int = 0
    section: str = ""
    course_id: int = 0


class AttendanceReportRepository(Protocol):
    """Interface that Zakia's report service requires from the data layer."""

    async def list_report_rows(
        self,
        filters: AttendanceReportFilters,
    ) -> list[AttendanceReportRow]:
        """Return filtered rows containing the latest corrections.

        Args:
            filters: Validated report filters.

        Returns:
            Effective attendance rows matching all selected filters.
        """

        ...


class InMemoryAttendanceReportRepository:
    """Filter attendance rows without requiring the shared database yet."""

    def __init__(self, rows: list[AttendanceReportRow]) -> None:
        """Store the rows used by the report workflow.

        Args:
            rows: Effective attendance records available for searching.
        """

        self._rows = rows

    async def list_report_rows(
        self,
        filters: AttendanceReportFilters,
    ) -> list[AttendanceReportRow]:
        """Return rows that match every selected report filter.

        Args:
            filters: Validated department, course, student, and date filters.

        Returns:
            Matching rows in their original order.
        """

        return [
            row
            for row in self._rows
            if row.department.casefold() == filters.department.casefold()
            and row.batch == filters.batch
            and row.section.casefold() == filters.section.casefold()
            and row.course_id == filters.course_id
            and (
                filters.student_id is None
                or row.student_id == filters.student_id
            )
            and filters.start_date
            <= row.recorded_at.date()
            <= filters.end_date
        ]


class PostgreSQLAttendanceReportRepository:
    """Read filtered attendance rows from the shared PostgreSQL database."""

    def __init__(self, session: AsyncSession) -> None:
        """Store the database session used by this request.

        Args:
            session: Shared asynchronous SQLAlchemy session.
        """

        self._session = session

    async def list_report_rows(
        self,
        filters: AttendanceReportFilters,
    ) -> list[AttendanceReportRow]:
        """Return effective attendance records matching every filter.

        Args:
            filters: Validated report filters.

        Returns:
            Filtered rows used by the report service.
        """

        statement = text(
            """
            SELECT
                students.id AS student_id,
                students.student_number,
                students.full_name AS student_name,
                attendance_records.status,
                attendance_records.attendance_value,
                attendance_records.recorded_at,
                attendance_records.modified_at,
                departments.code AS department,
                course_offerings.batch,
                course_offerings.section,
                course_offerings.course_id
            FROM attendance_records
            JOIN students
                ON students.id = attendance_records.student_id
            JOIN departments
                ON departments.id = students.department_id
            JOIN attendance_sessions
                ON attendance_sessions.id = attendance_records.session_id
            JOIN course_offerings
                ON course_offerings.id = attendance_sessions.offering_id
            WHERE LOWER(departments.code) = LOWER(:department)
                AND course_offerings.batch = :batch
                AND LOWER(course_offerings.section) = LOWER(:section)
                AND course_offerings.course_id = :course_id
                AND (
                    CAST(:student_id AS BIGINT) IS NULL
                    OR students.id = CAST(:student_id AS BIGINT)
                )
                AND attendance_sessions.scheduled_start >= :start_at
                AND attendance_sessions.scheduled_start < :end_at
            ORDER BY
                students.student_number,
                attendance_sessions.scheduled_start
            """
        )
        start_at = datetime.combine(
            filters.start_date,
            time.min,
            tzinfo=UTC,
        )
        end_at = datetime.combine(
            filters.end_date + timedelta(days=1),
            time.min,
            tzinfo=UTC,
        )
        result = await self._session.execute(
            statement,
            {
                "department": filters.department,
                "batch": filters.batch,
                "section": filters.section,
                "course_id": filters.course_id,
                "student_id": filters.student_id,
                "start_at": start_at,
                "end_at": end_at,
            },
        )

        return [
            AttendanceReportRow(
                student_id=row.student_id,
                student_number=row.student_number,
                student_name=row.student_name,
                status=row.status,
                attendance_value=float(row.attendance_value),
                recorded_at=row.recorded_at,
                modified_at=row.modified_at,
                department=row.department,
                batch=row.batch,
                section=row.section,
                course_id=row.course_id,
            )
            for row in result.mappings()
        ]
