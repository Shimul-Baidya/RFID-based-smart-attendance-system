"""Student database model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.rfid_model import RFIDCard


class Student(Base):
    """Represent one student profile."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "batch",
            "student_number",
            name="uq_student_roll_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_number: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    registration_number: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    program_id: Mapped[int] = mapped_column(Integer, nullable=False)
    batch: Mapped[int] = mapped_column(Integer, nullable=False)
    academic_session: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )
    semester: Mapped[str] = mapped_column(String(3), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(254),
        unique=True,
    )
    phone: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )

    rfid_cards: Mapped[list[RFIDCard]] = relationship(
        back_populates="student",
    )
