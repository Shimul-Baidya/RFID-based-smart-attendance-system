from fastapi import APIRouter

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
async def get_user_notifications(
    user_id: int,
) -> list[NotificationResponse]:
    """Return the notifications for a user's dashboard."""
    return await notification_service.get_user_notifications(
        user_id
    )