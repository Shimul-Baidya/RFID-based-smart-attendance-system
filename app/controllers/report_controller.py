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

router = APIRouter(prefix="/reports", tags=["Reports"])


@dataclass(frozen=True, slots=True)
class ReportUser:
    """Minimal shared-auth contract needed by this feature."""

    id: int
    role: str


def get_current_report_user() -> ReportUser:
    """Provide the authenticated user through the shared authentication layer.

    Returns:
        The authenticated user's minimum report-access details.

    Raises:
        HTTPException: Until the shared authentication dependency is connected.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shared authentication dependency is not connected yet.",
    )


def get_attendance_report_repository() -> AttendanceReportRepository:
    """Provide the shared PostgreSQL attendance-report repository.

    Returns:
        The configured attendance-report repository.

    Raises:
        HTTPException: Until the shared repository is connected.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shared attendance repository is not connected yet.",
    )


@router.get(
    "/attendance",
    response_model=AttendanceReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Filter and search attendance reports",
)
async def get_attendance_report(
    filters: Annotated[AttendanceReportFilters, Depends()],
    current_user: Annotated[ReportUser, Depends(get_current_report_user)],
    repository: Annotated[
        AttendanceReportRepository,
        Depends(get_attendance_report_repository),
    ],
) -> AttendanceReportResponse:
    """Generate an attendance report for an authorized teacher or admin.

    Args:
        filters: Validated query parameters for the report search.
        current_user: User supplied by the authentication dependency.
        repository: Attendance data-access implementation.

    Returns:
        A paginated attendance report response.

    Raises:
        HTTPException: If the authenticated user lacks report permission.
    """

    if current_user.role not in {"teacher", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and administrators can access reports.",
        )
    return await AttendanceReportService(repository).generate(filters)
