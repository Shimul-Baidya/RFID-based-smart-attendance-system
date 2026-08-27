"""Export the student and RFID database models."""

from app.models.rfid_model import RFIDCard
from app.models.student_model import Student

__all__ = ["RFIDCard", "Student"]
