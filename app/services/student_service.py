"""Business rules for student profiles and RFID assignment."""

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import RFIDCard, Student
from app.schemas.student_schema import (
    RFIDAssign,
    StudentCreate,
    normalize_rfid_uid,
)


class StudentRFIDService:
    """Handle only student-profile and RFID-assignment operations."""

    def __init__(self, database: Session) -> None:
        """Receive the database dependency used by this service."""

        self.database = database

    def create_student(self, data: StudentCreate) -> Student:
        """Create a student when its unique fields are unused."""

        duplicate_conditions = [
            and_(
                Student.program_id == data.program_id,
                Student.batch == data.batch,
                Student.student_number == data.student_number,
            ),
            Student.registration_number == data.registration_number,
        ]
        if data.email is not None:
            duplicate_conditions.append(Student.email == data.email)

        duplicate = self.database.scalar(
            select(Student).where(or_(*duplicate_conditions))
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Roll for this program and batch, registration number, "
                    "or email already exists"
                ),
            )

        student = Student(**data.model_dump())
        self.database.add(student)
        self._save_changes(
            "Student profile conflicts with existing data"
        )
        self.database.refresh(student)
        return student

    def get_student_by_id(self, student_id: int) -> Student:
        """Return one student using the database primary key."""

        student = self.database.get(Student, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        return student

    def search_students(self, query: str) -> list[Student]:
        """Search students by name, roll, or registration number."""

        search_value = f"%{query.strip()}%"
        statement = (
            select(Student)
            .where(
                or_(
                    Student.full_name.ilike(search_value),
                    Student.student_number.ilike(search_value),
                    Student.registration_number.ilike(search_value),
                )
            )
            .order_by(Student.full_name)
            .limit(20)
        )
        return list(self.database.scalars(statement).all())

    def assign_rfid(
        self,
        student_id: int,
        data: RFIDAssign,
    ) -> RFIDCard:
        """Assign one unused RFID UID to one active student."""

        student = self.database.get(Student, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        if student.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student is not active",
            )

        existing_uid = self.database.scalar(
            select(RFIDCard).where(RFIDCard.uid == data.uid)
        )
        if existing_uid is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="RFID UID is already assigned",
            )

        active_card = self.database.scalar(
            select(RFIDCard).where(
                RFIDCard.student_id == student_id,
                RFIDCard.status == "active",
            )
        )
        if active_card is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student already has an active RFID card",
            )

        card = RFIDCard(uid=data.uid, student_id=student_id)
        self.database.add(card)
        self._save_changes(
            "RFID assignment conflicts with existing data"
        )
        self.database.refresh(card)
        return card

    def find_student_by_rfid_uid(self, uid: str) -> Student:
        """Return the active student assigned to an active RFID UID."""

        try:
            normalized_uid = normalize_rfid_uid(uid)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error

        student = self.database.scalar(
            select(Student)
            .join(RFIDCard)
            .where(
                RFIDCard.uid == normalized_uid,
                RFIDCard.status == "active",
                Student.status == "active",
            )
        )
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active student not found for this RFID UID",
            )
        return student

    def _save_changes(self, conflict_message: str) -> None:
        """Commit one transaction or convert a conflict to HTTP 409."""

        try:
            self.database.commit()
        except IntegrityError as error:
            self.database.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_message,
            ) from error
