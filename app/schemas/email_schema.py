"""Schemas for composing attendance-update emails."""

from pydantic import BaseModel, EmailStr


class AttendanceEmailData(BaseModel):
    """Data needed to compose an attendance-update email."""

    student_name: str
    student_email: EmailStr
    course_name: str
    class_date: str
    attendance_status: str
    instructions: str | None = None
   