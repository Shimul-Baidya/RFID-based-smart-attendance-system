"""Schemas for RFID attendance requests."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AttendanceScanRequest(BaseModel):
    """
    Represent a simulated RFID attendance scan request.

    Attributes:
        rfid_uid (str): Unique identifier of the RFID card.
        session_id (int): Identifier of the active class session.
    """

    rfid_uid: str = Field(min_length=1, max_length=64)
    session_id: int = Field(gt=0)

    @field_validator("rfid_uid")
    @classmethod
    def normalize_rfid_uid(cls, value: str) -> str:
        """
        Normalize the RFID UID.

        Args:
            value (str): RFID UID received from the scan request.

        Returns:
            str: RFID UID without surrounding spaces and in uppercase.

        Raises:
            ValueError: If the RFID UID is empty after removing spaces.
        """
        normalized_uid = value.strip().upper()

        if not normalized_uid:
            raise ValueError("RFID UID must not be empty")

        return normalized_uid


class AttendanceScanResponse(BaseModel):
    """
    Represent a successful RFID attendance response.

    Attributes:
        message (str): Message describing the attendance result.
        attendance_id (int): Unique identifier of the attendance record.
        student_id (int): Unique identifier of the student.
        session_id (int): Unique identifier of the class session.
        course_id (int): Course code associated with the session.
        status (Literal["present", "late"]): Recorded attendance status.
        duplicate (bool): Whether the attendance was previously recorded.
        recorded_at (datetime): Date and time of the attendance record.
    """

    message: str
    attendance_id: int = Field(gt=0)
    student_id: int = Field(gt=0)
    session_id: int = Field(gt=0)
    course_id: int = Field(ge=100, le=999)
    status: Literal["present", "late"]
    duplicate: bool
    recorded_at: datetime