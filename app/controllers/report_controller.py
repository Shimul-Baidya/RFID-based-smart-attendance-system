"""FastAPI controller for attendance report filtering."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.attendance_repository import AttendanceReportRepository
from app.schemas.report_schema import (
    AttendanceReportFilters,
    AttendanceReportResponse,
)
from app.services.report_service import AttendanceReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@dataclass(frozen=True, slots=True)
class ReportUser:
    """Minimal shared-auth contract needed by this feature."""

    id: int
    role: str


def get_current_report_user() -> ReportUser:
    """Temporary seam for Shimul's shared authentication dependency."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shared authentication dependency is not connected yet.",
    )


def get_attendance_report_repository() -> AttendanceReportRepository:
    """Temporary seam for the shared PostgreSQL repository implementation."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shared attendance repository is not connected yet.",
    )


@router.get("/attendance", response_model=AttendanceReportResponse)
async def get_attendance_report(
    filters: Annotated[AttendanceReportFilters, Depends()],
    current_user: Annotated[ReportUser, Depends(get_current_report_user)],
    repository: Annotated[
        AttendanceReportRepository,
        Depends(get_attendance_report_repository),
    ],
) -> AttendanceReportResponse:
    """Generate an attendance report for an authorized teacher or admin."""

    if current_user.role not in {"teacher", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and administrators can access reports.",
        )
    return await AttendanceReportService(repository).generate(filters)
