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
