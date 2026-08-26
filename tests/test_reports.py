"""Tests for Zakia's attendance report filtering workflow."""

import asyncio
from collections.abc import Iterator
from datetime import UTC, date, datetime

import pytest
from httpx import ASGITransport, AsyncClient, Response
from pydantic import ValidationError

from app.controllers.report_controller import (
    ReportUser,
    get_attendance_report_repository,
    get_current_report_user,
)
from app.main import app
from app.repositories.attendance_repository import (
    AttendanceReportRow,
    InMemoryAttendanceReportRepository,
)
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


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    """Remove FastAPI dependency overrides after every endpoint test.

    Yields:
        Control to the test while dependency overrides are active.
    """

    yield
    app.dependency_overrides.clear()


def test_invalid_date_range_is_rejected() -> None:
    with pytest.raises(ValidationError, match="end_date must be"):
        make_filters(
            start_date=date(2026, 8, 23),
            end_date=date(2026, 8, 22),
        )


def test_missing_required_filter_is_rejected() -> None:
    with pytest.raises(ValidationError, match="department"):
        AttendanceReportFilters(
            batch=2023,
            section="A",
            course_id=10,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 23),
        )


def test_fractional_attendance_and_threshold_are_calculated() -> None:
    now = datetime(2026, 8, 23, tzinfo=UTC)
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
    assert response.message == (
        "No attendance data found for the selected filters."
    )


def test_corrected_attendance_value_appears_in_result() -> None:
    recorded_at = datetime(2026, 8, 20, tzinfo=UTC)
    modified_at = datetime(2026, 8, 23, tzinfo=UTC)
    corrected_row = AttendanceReportRow(
        1,
        "CSE-001",
        "Zakia",
        "present",
        1.0,
        recorded_at,
        modified_at,
    )

    response = asyncio.run(
        AttendanceReportService(
            FakeAttendanceRepository([corrected_row])
        ).generate(make_filters())
    )

    assert response.items[0].attendance_percentage == 100.0
    assert response.items[0].latest_attendance_at == modified_at


def test_results_are_paginated() -> None:
    now = datetime(2026, 8, 23, tzinfo=UTC)
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


def test_repository_returns_only_matching_records() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)
    rows = [
        AttendanceReportRow(
            1,
            "CSE-001",
            "Zakia",
            "present",
            1.0,
            now,
            department="CSE",
            batch=2023,
            section="A",
            course_id=10,
        ),
        AttendanceReportRow(
            2,
            "CSE-002",
            "Student Two",
            "present",
            1.0,
            now,
            department="CSE",
            batch=2023,
            section="A",
            course_id=10,
        ),
        AttendanceReportRow(
            3,
            "CSE-003",
            "Old Record",
            "present",
            1.0,
            datetime(2026, 7, 20, tzinfo=UTC),
            department="CSE",
            batch=2023,
            section="A",
            course_id=10,
        ),
    ]
    repository = InMemoryAttendanceReportRepository(rows)

    result = asyncio.run(repository.list_report_rows(make_filters()))

    searched_result = asyncio.run(
        repository.list_report_rows(make_filters(student_id=2))
    )

    assert [row.student_id for row in result] == [1, 2]
    assert [row.student_id for row in searched_result] == [2]


def test_endpoint_returns_filtered_attendance_summary() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)
    rows = [
        AttendanceReportRow(
            1,
            "CSE-001",
            "Zakia",
            "present",
            1.0,
            now,
            department="CSE",
            batch=2023,
            section="A",
            course_id=10,
        ),
        AttendanceReportRow(
            1,
            "CSE-001",
            "Zakia",
            "absent",
            0.0,
            now,
            department="CSE",
            batch=2023,
            section="A",
            course_id=10,
        ),
    ]
    app.dependency_overrides[get_current_report_user] = lambda: ReportUser(
        id=1,
        role="teacher",
    )
    app.dependency_overrides[get_attendance_report_repository] = lambda: (
        InMemoryAttendanceReportRepository(rows)
    )

    response = asyncio.run(request_report())

    assert response.status_code == 200
    report = response.json()
    assert report["total_items"] == 1
    assert report["items"][0]["present"] == 1
    assert report["items"][0]["absent"] == 1
    assert report["items"][0]["attendance_percentage"] == 50.0


def test_student_cannot_access_report_endpoint() -> None:
    app.dependency_overrides[get_current_report_user] = lambda: ReportUser(
        id=1,
        role="student",
    )
    app.dependency_overrides[get_attendance_report_repository] = lambda: (
        FakeAttendanceRepository([])
    )

    response = asyncio.run(request_report())

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Only teachers and administrators can access reports."
    )


@pytest.mark.parametrize("role", ["teacher", "admin"])
def test_authorized_user_can_access_report_endpoint(role: str) -> None:
    app.dependency_overrides[get_current_report_user] = lambda: ReportUser(
        id=1,
        role=role,
    )
    app.dependency_overrides[get_attendance_report_repository] = lambda: (
        FakeAttendanceRepository([])
    )

    response = asyncio.run(request_report())

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_openapi_contains_attendance_report_endpoint() -> None:
    openapi_schema = app.openapi()

    assert "/reports/attendance" in openapi_schema["paths"]
    operation = openapi_schema["paths"]["/reports/attendance"]["get"]
    assert "Reports" in operation["tags"]


async def request_report() -> Response:
    """Request the report endpoint through an in-process ASGI transport.

    Returns:
        The HTTP response produced by the FastAPI application.
    """

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(
            "/reports/attendance",
            params={
                "department": "CSE",
                "batch": 2023,
                "section": "A",
                "course_id": 10,
                "start_date": "2026-08-01",
                "end_date": "2026-08-23",
            },
        )
