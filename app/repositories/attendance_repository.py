"""Repository boundary used by attendance report generation.

The concrete PostgreSQL repository will be connected after the shared database
session and attendance models are merged. Keeping this boundary small prevents
report business rules from leaking into controllers or database code.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

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
