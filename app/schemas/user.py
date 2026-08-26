# Pydantic models for user‑related data
"""User request/response schemas.

These models are deliberately simple – the academic project only needs an
email and a password for registration and login.  The ``UserCreate`` schema is
used for the request body when a new user signs up; ``UserResponse`` mirrors the
data you’d return after a successful registration (without the password).
"""

from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain‑text password")

class UserResponse(UserBase):
    id: int = Field(..., description="Unique identifier for the user")

    class Config:
        orm_mode = True

