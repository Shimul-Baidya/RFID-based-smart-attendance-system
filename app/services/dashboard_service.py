from typing import Dict, List

from app.core.permissions import check_role_permission
from app.schemas.dashboard_schema import DashboardResponse


# Dashboard actions available for each role.
# These permissions define what users can see or do
# from their respective dashboards.
ROLE_ACTIONS: Dict[str, List[str]] = {
    "admin": [
        "manage_users",
        "manage_students",
        "manage_rfid",
        "view_reports",
        "view_attendance",
    ],
    "teacher": [
        "view_attendance",
        "view_reports",
    ],
    "staff": [
        "manage_students",
        "manage_rfid",
        "view_attendance",
    ],
    "student": [
        "view_attendance",
        "view_notifications",
    ],
}


def get_dashboard(
    user_name: str,
    user_role: str,
) -> DashboardResponse:
    """
    Generate dashboard data based on the user's role.

    The service validates the user's role and returns only
    the actions permitted for that role.

    Args:
        user_name: Name of the current user.
        user_role: Role of the current user.

    Returns:
        DashboardResponse containing the user's role,
        name, and permitted dashboard actions.

    Raises:
        HTTPException: If the user's role is invalid.
    """

    # Check whether the provided role is valid.
    check_role_permission(
        user_role=user_role,
        allowed_roles=ROLE_ACTIONS.keys(),
    )

    # Get the actions assigned to the user's role.
    allowed_actions = ROLE_ACTIONS[user_role]

    # Return the dashboard response.
    return DashboardResponse(
        role=user_role,
        user_name=user_name,
        allowed_actions=allowed_actions,
    )