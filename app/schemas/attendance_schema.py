"""Schemas for RFID attendance requests."""

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
