"""Request and response schemas for students and RFID cards."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_rfid_uid(uid: str) -> str:
    """Remove scanner separators and return one standard UID."""

    normalized = uid.replace(":", "").replace("-", "")
    normalized = normalized.strip().upper()
    if len(normalized) < 4 or not normalized.isalnum():
        message = (
            "RFID UID must contain at least four letters or numbers"
        )
        raise ValueError(message)
    return normalized


class StudentCreate(BaseModel):
    """Validate data used to create a student profile."""

    student_number: str = Field(min_length=1, max_length=40)
    registration_number: str = Field(min_length=1, max_length=60)
    full_name: str = Field(min_length=1, max_length=120)
    department_id: int = Field(gt=0)
    program_id: int = Field(gt=0)
    batch: int = Field(ge=1, le=100)
    academic_session: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}$")
    semester: str = Field(pattern=r"^[1-4]-[1-2]$")
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=30)
    status: str = Field(
        default="active",
        pattern=r"^(active|inactive|graduated|suspended)$",
    )

    @field_validator(
        "student_number",
        "registration_number",
        "full_name",
        "academic_session",
        "semester",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        """Remove unnecessary surrounding spaces."""

        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        """Normalize and perform simple email validation."""

        if value is None:
            return None
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("A valid email is required")
        return normalized


class StudentResponse(BaseModel):
    """Student fields returned to an API client."""

    id: int
    student_number: str
    registration_number: str
    full_name: str
    department_id: int
    program_id: int
    batch: int
    academic_session: str
    semester: str
    email: str | None
    phone: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class RFIDAssign(BaseModel):
    """Validate an RFID UID submitted for assignment."""

    uid: str = Field(min_length=4, max_length=128)

    @field_validator("uid")
    @classmethod
    def validate_uid(cls, value: str) -> str:
        """Return the normalized RFID UID."""

        return normalize_rfid_uid(value)


class RFIDResponse(BaseModel):
    """RFID fields returned to an API client."""

    id: int
    uid: str
    student_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
