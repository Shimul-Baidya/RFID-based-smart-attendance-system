from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.schemas.dashboard_schema import DashboardResponse
from app.services.dashboard_service import get_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/", response_model=DashboardResponse)
def get_user_dashboard(
    user_name: Optional[str] = None,
    user_role: Optional[str] = None,
) -> DashboardResponse:
    """
    Return the dashboard based on the user's role.

    This endpoint currently uses temporary user inputs
    for development until the authentication module is integrated.

    Args:
        user_name: Name of the current user.
        user_role: Role of the current user.

    Returns:
        DashboardResponse containing role-specific
        dashboard information.

    Raises:
        HTTPException: If user credentials are missing.
    """

    # Check whether the required user information is provided.
    # In the final implementation, this will be handled
    # by the shared authentication dependency.
    if not user_name or not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    return get_dashboard(
        user_name=user_name,
        user_role=user_role,
    )