from typing import List
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.services.auth import get_current_user

# Temporary: uses get_current_user from app.services.auth.
# Replace with the finalized get_current_user dependency when available.

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user
    return role_checker

