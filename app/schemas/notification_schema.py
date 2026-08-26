from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    student_id: int
    attendance_id: int
    course_name: str
    class_time: str
    class_date: datetime
    punch_time: datetime
    attendance_status: str


class NotificationResponse(BaseModel):
    id: int
    course_name: str
    class_time: str
    class_date: datetime
    punch_time: datetime
    attendance_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)