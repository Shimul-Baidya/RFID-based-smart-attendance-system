from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError

from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.services.security import verify_password, DUMMY_HASH, SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """
    Dependency to retrieve the currently authenticated user from the request token.

    This function extracts the JWT from the ``Authorization`` header, decodes it
    using the application's secret key, and retrieves the user record from the
    database. It is used to protect routes that require authentication.

    Args:
        token (str): The JWT access token provided in the request header.
        db (Session): The database session dependency.

    Returns:
        User: The authenticated user's database record.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

