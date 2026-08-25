"""Unit tests for Zakia's Sprint 1 attendance report contracts."""

import asyncio
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.repositories.attendance_repository import AttendanceReportRow
from app.schemas.report_schema import AttendanceReportFilters
from app.services.report_service import AttendanceReportService


def make_filters(**changes: object) -> AttendanceReportFilters:
    """Create a valid filter object with optional field overrides."""

    data = {
        "department": "CSE",
        "batch": 2023,
        "section": "A",
        "course_id": 10,
        "start_date": date(2026, 8, 1),
        "end_date": date(2026, 8, 23),
    }
    data.update(changes)
    return AttendanceReportFilters(**data)


class FakeAttendanceRepository:
    """In-memory replacement for the shared repository dependency."""

    def __init__(self, rows: list[AttendanceReportRow]) -> None:
        self.rows = rows

    async def list_report_rows(
        self,
        filters: AttendanceReportFilters,
    ) -> list[AttendanceReportRow]:
        return self.rows


def test_invalid_date_range_is_rejected() -> None:
    with pytest.raises(ValidationError, match="end_date must be"):
        make_filters(
            start_date=date(2026, 8, 23),
            end_date=date(2026, 8, 22),
        )


def test_fractional_attendance_and_threshold_are_calculated() -> None:
    now = datetime(2026, 8, 23, tzinfo=timezone.utc)
    rows = [
        AttendanceReportRow(1, "CSE-001", "Zakia", "present", 1.0, now),
        AttendanceReportRow(1, "CSE-001", "Zakia", "late", 0.5, now),
        AttendanceReportRow(
            1,
            "CSE-001",
            "Zakia",
            "fractional",
            0.5,
            now,
        ),
        AttendanceReportRow(1, "CSE-001", "Zakia", "absent", 0.0, now),
    ]

    response = asyncio.run(
        AttendanceReportService(FakeAttendanceRepository(rows)).generate(
            make_filters()
        )
    )

    assert response.total_items == 1
    assert response.items[0].attendance_percentage == 50.0
    assert response.items[0].fractional_attendance == 0.5
    assert response.items[0].is_below_threshold is True


def test_empty_result_has_clear_message() -> None:
    response = asyncio.run(
        AttendanceReportService(FakeAttendanceRepository([])).generate(
            make_filters()
        )
    )

    assert response.items == []
    assert response.total_pages == 0
    assert response.message == "No attendance data found for the selected filters."


def test_results_are_paginated() -> None:
    now = datetime(2026, 8, 23, tzinfo=timezone.utc)
    rows = [
        AttendanceReportRow(
            student_id,
            f"CSE-{student_id:03}",
            f"Student {student_id}",
            "present",
            1.0,
            now,
        )
        for student_id in range(1, 4)
    ]

    response = asyncio.run(
        AttendanceReportService(FakeAttendanceRepository(rows)).generate(
            make_filters(page=2, page_size=2)
        )
    )

    assert response.total_items == 3
    assert response.total_pages == 2
    assert [item.student_id for item in response.items] == [3]
