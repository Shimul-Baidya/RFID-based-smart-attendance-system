"""Business rules for filtered attendance reports."""

from collections import defaultdict
from dataclasses import dataclass, field
from math import ceil

from app.repositories.attendance_repository import (
    AttendanceReportRepository,
    AttendanceReportRow,
)
from app.schemas.report_schema import (
    AttendanceReportFilters,
    AttendanceReportItem,
    AttendanceReportResponse,
)

DEFAULT_LOW_ATTENDANCE_THRESHOLD = 75.0


@dataclass(slots=True)
class _StudentSummary:
    """Mutable accumulator used while aggregating attendance rows."""

    student_number: str
    student_name: str
    rows: list[AttendanceReportRow] = field(default_factory=list)


class AttendanceReportService:
    """Generate paginated student summaries from effective attendance rows."""

    def __init__(
        self,
        repository: AttendanceReportRepository,
        low_attendance_threshold: float = DEFAULT_LOW_ATTENDANCE_THRESHOLD,
    ) -> None:
        if not 0 <= low_attendance_threshold <= 100:
            raise ValueError("low_attendance_threshold must be between 0 and 100")
        self._repository = repository
        self._threshold = low_attendance_threshold

    async def generate(
        self,
        filters: AttendanceReportFilters,
    ) -> AttendanceReportResponse:
        """Return the filtered report using corrected attendance values."""

        rows = await self._repository.list_report_rows(filters)
        summaries = self._summarize(rows)
        total_items = len(summaries)
        start = (filters.page - 1) * filters.page_size
        end = start + filters.page_size

        return AttendanceReportResponse(
            message=(
                "Attendance report generated successfully."
                if summaries
                else "No attendance data found for the selected filters."
            ),
            items=summaries[start:end],
            page=filters.page,
            page_size=filters.page_size,
            total_items=total_items,
            total_pages=ceil(total_items / filters.page_size),
            low_attendance_threshold=self._threshold,
        )

    def _summarize(
        self,
        rows: list[AttendanceReportRow],
    ) -> list[AttendanceReportItem]:
        grouped: dict[int, _StudentSummary] = defaultdict(
            lambda: _StudentSummary(student_number="", student_name="")
        )
        for row in rows:
            summary = grouped[row.student_id]
            summary.student_number = row.student_number
            summary.student_name = row.student_name
            summary.rows.append(row)

        result = []
        for student_id, summary in grouped.items():
            total_classes = len(summary.rows)
            earned = sum(float(row.attendance_value) for row in summary.rows)
            percentage = (
                round((earned / total_classes) * 100, 2)
                if total_classes
                else 0.0
            )
            result.append(
                AttendanceReportItem(
                    student_id=student_id,
                    student_number=summary.student_number,
                    student_name=summary.student_name,
                    total_classes=total_classes,
                    present=sum(row.status == "present" for row in summary.rows),
                    absent=sum(row.status == "absent" for row in summary.rows),
                    late=sum(row.status == "late" for row in summary.rows),
                    fractional_attendance=round(
                        sum(
                            float(row.attendance_value)
                            for row in summary.rows
                            if row.status == "fractional"
                        ),
                        2,
                    ),
                    attendance_percentage=percentage,
                    is_below_threshold=percentage < self._threshold,
                    latest_attendance_at=max(
                        (row.modified_at or row.recorded_at)
                        for row in summary.rows
                    ),
                )
            )

        return sorted(result, key=lambda item: item.student_number)
