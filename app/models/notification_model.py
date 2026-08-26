from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

# TODO: uncomment once app/database (Base) is created by the team
# from app.database import Base


class AttendanceNotification:  # TODO: change to (Base) once Base is available
    __tablename__ = "attendance_notifications"

    id = Column(Integer, primary_key=True)
    student_id = Column(
        Integer,
        ForeignKey("students.id"),  # TODO: confirm table name once student model exists
        nullable=False,
    )
    attendance_id = Column(
        Integer,
        ForeignKey("attendance_records.id"),  # TODO: confirm table name
        nullable=False,
        unique=True,
    )
    course_name = Column(String(100), nullable=False)
    class_time = Column(String(50), nullable=False)
    class_date = Column(DateTime, nullable=False)
    punch_time = Column(DateTime, nullable=False)
    attendance_status = Column(String(20), nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    student = relationship("Student")