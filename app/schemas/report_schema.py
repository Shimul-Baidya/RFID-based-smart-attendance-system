"""Pydantic contracts for attendance report filtering and responses."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttendanceReportFilters(BaseModel):
    """Validate the filters accepted by the attendance report endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    department: str = Field(
        min_length=1,
        max_length=120,
        description="Department code or name used to filter students.",
        examples=["CSE"],
    )
    batch: int = Field(
        ge=2000,
        le=2100,
        description="Student batch year.",
        examples=[2023],
    )
    section: str = Field(
        min_length=1,
        max_length=20,
        description="Course-offering section.",
        examples=["A"],
    )
    course_id: int = Field(
        gt=0,
        description="Unique course identifier.",
        examples=[10],
    )
    student_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional student identifier for a single-student report.",
        examples=[125],
    )
    start_date: date = Field(
        description="First date included in the report.",
        examples=["2026-08-01"],
    )
    end_date: date = Field(
        description="Last date included in the report.",
        examples=["2026-08-23"],
    )
    page: int = Field(
        default=1,
        ge=1,
        description="One-based result page number.",
        examples=[1],
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum students returned per page.",
        examples=[20],
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "AttendanceReportFilters":
        """Reject a report whose end date is before its start date."""

        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class AttendanceReportItem(BaseModel):
    """Aggregated attendance information for one student."""

    student_id: int = Field(description="Internal student identifier.")
    student_number: str = Field(description="Institutional student number.")
    student_name: str = Field(description="Student's full name.")
    total_classes: int = Field(
        ge=0,
        description="Number of selected attendance sessions.",
    )
    present: int = Field(ge=0, description="Number of present records.")
    absent: int = Field(ge=0, description="Number of absent records.")
    late: int = Field(ge=0, description="Number of late records.")
    fractional_attendance: float = Field(
        ge=0,
        description="Sum of fractional attendance values.",
    )
    attendance_percentage: float = Field(
        ge=0,
        le=100,
        description="Earned attendance as a percentage of total classes.",
    )
    is_below_threshold: bool = Field(
        description="Whether attendance is below the configured threshold."
    )
    latest_attendance_at: datetime | None = Field(
        default=None,
        description="Most recent recording or correction time.",
    )


class AttendanceReportResponse(BaseModel):
    """Paginated response returned for an attendance report search."""

    message: str = Field(description="Human-readable report result.")
    items: list[AttendanceReportItem] = Field(
        description="Student attendance summaries for the requested page."
    )
    page: int = Field(ge=1, description="Current page number.")
    page_size: int = Field(ge=1, description="Maximum items per page.")
    total_items: int = Field(ge=0, description="Total matching students.")
    total_pages: int = Field(ge=0, description="Total available pages.")
    low_attendance_threshold: float = Field(
        ge=0,
        le=100,
        description="Percentage below which attendance is considered low.",
    )
