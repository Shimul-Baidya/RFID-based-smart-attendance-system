from typing import List

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    """
    Response structure for a role-based dashboard.

    This schema defines the common information that can be
    returned when a user accesses their dashboard.
    """

    # The role of the currently authenticated user.
    role: str

    # Display name of the current user.
    user_name: str

    # List of actions available to the current user.
    allowed_actions: List[str]