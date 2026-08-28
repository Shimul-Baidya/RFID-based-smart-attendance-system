"""FastAPI endpoints for student profiles and RFID assignment."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RFIDCard, Student
from app.schemas.student_schema import (
    RFIDAssign,
    RFIDResponse,
    StudentCreate,
    StudentResponse,
)
from app.services.student_service import StudentRFIDService

router = APIRouter(
    prefix="/students",
    tags=["Students and RFID"],
)


@router.get(
    "/search",
    response_model=list[StudentResponse],
)
def search_students(
    query: str = Query(min_length=1, max_length=120),
    database: Session = Depends(get_db),
) -> list[Student]:
    """Search students by name, roll, or registration number."""

    service = StudentRFIDService(database)
    return service.search_students(query)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    data: StudentCreate,
    database: Session = Depends(get_db),
) -> Student:
    """Create one student profile."""

    service = StudentRFIDService(database)
    return service.create_student(data)


@router.post(
    "/{student_id}/rfid",
    response_model=RFIDResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_rfid(
    student_id: int,
    data: RFIDAssign,
    database: Session = Depends(get_db),
) -> RFIDCard:
    """Assign one simulated RFID UID to a student."""

    service = StudentRFIDService(database)
    return service.assign_rfid(student_id, data)


@router.get(
    "/by-rfid/{uid}",
    response_model=StudentResponse,
)
def find_student_by_rfid(
    uid: str,
    database: Session = Depends(get_db),
) -> Student:
    """Find a student using an active RFID UID."""

    service = StudentRFIDService(database)
    return service.find_student_by_rfid_uid(uid)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
)
def get_student(
    student_id: int,
    database: Session = Depends(get_db),
) -> Student:
    """Return one student using its database ID."""

    service = StudentRFIDService(database)
    return service.get_student_by_id(student_id)
