from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.token import Token
from app.services.auth import authenticate_user
from app.services.security import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["Authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT access token.

    This endpoint accepts an OAuth2 form containing a username and password,
    verifies the credentials against the database, and if successful, generates
    and returns a JSON Web Token (JWT) that can be used for accessing protected
    routes.

    Args:
        form_data (OAuth2PasswordRequestForm): The username and password submitted by the client.
        db (Session): The database session dependency.

    Returns:
        Token: A Pydantic model containing the ``access_token`` and ``token_type``.

    Raises:
        HTTPException: 401 Unauthorized if the credentials are invalid.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

