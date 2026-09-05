from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notification_schema import NotificationResponse
from app.services import notification_service


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "/users/{user_id}",
    response_model=list[NotificationResponse],
)
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    """Return the notifications for a user's dashboard."""
    return notification_service.get_user_notifications(db, user_id)