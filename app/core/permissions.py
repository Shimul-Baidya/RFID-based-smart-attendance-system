from typing import Iterable

from fastapi import HTTPException, status


# Roles agreed upon by the project team.
# These are the only valid roles in the system.
VALID_ROLES = {
    "admin",
    "teacher",
    "staff",
    "student",
}


def validate_role(role: str) -> str:
    """
    Validate the role of the current user.

    This function checks whether a role exists and whether
    it is one of the valid roles defined by the project.

    Args:
        role: The role assigned to the current user.

    Returns:
        The validated role.

    Raises:
        HTTPException: If the role is missing or invalid.
    """

    # Reject the request if no role is provided.
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role is missing.",
        )

    # Reject roles that are not defined in the system.
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role.",
        )

    return role


def check_role_permission(
    user_role: str,
    allowed_roles: Iterable[str],
) -> bool:
    """
    Check whether the user's role is allowed to access a resource.

    This function is responsible only for authorization.
    Authentication, such as login and identifying the current
    user, will be handled by the authentication module.

    Args:
        user_role: Role of the current authenticated user.
        allowed_roles: Roles that are permitted to access
            the resource.

    Returns:
        True if the user has permission.

    Raises:
        HTTPException: If the user's role is invalid or
            does not have the required permission.
    """

    # First make sure the user's role is valid.
    user_role = validate_role(user_role)

    # Convert allowed roles to a set for easy membership checking.
    allowed_roles = set(allowed_roles)

    # If the user's role is not allowed, return 403 Forbidden.
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    # The user has the required permission.
    return True