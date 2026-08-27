"""Expose HTTP endpoints for RFID attendance scans."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.schemas.attendance_schema import (
    AttendanceScanRequest,
    AttendanceScanResponse,
)
from app.services.attendance_service import (
    AttendanceSessionClosedError,
    AttendanceSessionNotFoundError,
    DuplicateAttendanceError,
    RFIDCardNotFoundError,
    StudentNotEnrolledError,
    mark_attendance,
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)

DatabaseSession = Annotated[Session, Depends(get_database)]


@router.post(
    "/scan",
    response_model=AttendanceScanResponse,
    status_code=status.HTTP_201_CREATED,
)
def scan_attendance(
    request: AttendanceScanRequest,
    database: DatabaseSession,
) -> AttendanceScanResponse:
    """Record attendance from a simulated RFID scan.

    Args:
        request: Validated RFID scan and attendance-session data.
        database: Active SQLAlchemy database session.

    Returns:
        Details of the newly created attendance record.

    Raises:
        HTTPException: If the RFID card, session, enrollment, or
            attendance record is invalid.
    """
    try:
        return mark_attendance(
            database=database,
            rfid_uid=request.rfid_uid,
            session_id=request.session_id,
        )
    except RFIDCardNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except AttendanceSessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except AttendanceSessionClosedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except StudentNotEnrolledError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except DuplicateAttendanceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
