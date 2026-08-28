from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
    Text,
    TIMESTAMP,
    BigInteger,
)
from sqlalchemy.sql import func

# TODO(db-setup): uncomment once app/database provides Base
# from app.database import Base


class Notification:  # TODO(db-setup): change to (Base)
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )
    attendance_record_id = Column(
        BigInteger,
        ForeignKey("attendance_records.id"),
        nullable=True,
    )
    correction_request_id = Column(
        BigInteger,
        ForeignKey("attendance_correction_requests.id"),
        nullable=True,
    )
    report_export_id = Column(
        BigInteger,
        ForeignKey("report_exports.id"),
        nullable=True,
    )
    notification_type = Column(String(40), nullable=False)
    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)
    deduplication_key = Column(String(160), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    email_status = Column(
        String(20),
        nullable=False,
        default="not_requested",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    read_at = Column(TIMESTAMP(timezone=True), nullable=True)