from fastapi import APIRouter

from app.schemas.dashboard_schema import DashboardResponse
from app.services.dashboard_service import get_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/", response_model=DashboardResponse)
def get_user_dashboard(
    user_name: str,
    user_role: str,
) -> DashboardResponse:
    """
    Return the dashboard based on the user's role.

    This endpoint receives the user's role and passes it
    to the dashboard service to generate the appropriate
    dashboard response.

    Args:
        user_name: Name of the current user.
        user_role: Role of the current user.

    Returns:
        DashboardResponse containing role-specific
        dashboard information.
    """

    return get_dashboard(
        user_name=user_name,
        user_role=user_role,
    )