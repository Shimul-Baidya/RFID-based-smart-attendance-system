"""RFID-card database model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.student_model import Student


class RFIDCard(Base):
    """Represent an RFID card assigned to a student."""

    __tablename__ = "rfid_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )

    student: Mapped[Student] = relationship(
        back_populates="rfid_cards",
    )
