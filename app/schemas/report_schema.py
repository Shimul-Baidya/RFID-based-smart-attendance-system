"""Pydantic contracts for attendance report filtering and responses."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttendanceReportFilters(BaseModel):
    """Validate the filters accepted by the attendance report endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    department: str = Field(min_length=1, max_length=120)
    batch: int = Field(ge=2000, le=2100)
    section: str = Field(min_length=1, max_length=20)
    course_id: int = Field(gt=0)
    student_id: int | None = Field(default=None, gt=0)
    start_date: date
    end_date: date
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validate_date_range(self) -> "AttendanceReportFilters":
        """Reject a report whose end date is before its start date."""

        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class AttendanceReportItem(BaseModel):
    """Aggregated attendance information for one student."""

    student_id: int
    student_number: str
    student_name: str
    total_classes: int = Field(ge=0)
    present: int = Field(ge=0)
    absent: int = Field(ge=0)
    late: int = Field(ge=0)
    fractional_attendance: float = Field(ge=0)
    attendance_percentage: float = Field(ge=0, le=100)
    is_below_threshold: bool
    latest_attendance_at: datetime | None = None


class AttendanceReportResponse(BaseModel):
    """Paginated response returned for an attendance report search."""

    message: str
    items: list[AttendanceReportItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    low_attendance_threshold: float = Field(ge=0, le=100)
