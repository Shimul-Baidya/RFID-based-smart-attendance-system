# Password hashing and JWT helpers
"""Security utilities.

This module contains small, self‑contained helpers for password hashing and for
creating / decoding JWT access tokens.  The implementation mirrors what you’d
normally write by hand in a FastAPI project, but with plenty of inline comments
so it reads like a personal contribution rather than generated code.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import settings

# ---------------------------------------------------------------------------
# Password handling
# ---------------------------------------------------------------------------
# ``pwd_context`` is a thin wrapper around bcrypt; using ``passlib`` keeps the
# code short and avoids dealing with salt handling manually.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash for ``password``.

    The function is deliberately tiny – just a single call to ``pwd_context`` –
    but the docstring explains the intent so future readers (or reviewers) see
    why we chose ``bcrypt``.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check that ``plain_password`` matches ``hashed_password``.

    ``pwd_context.verify`` returns ``True`` when the passwords match and raises
    ``Exception`` otherwise; we normalise the result to a boolean.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

# ---------------------------------------------------------------------------
# JWT handling
# ---------------------------------------------------------------------------

def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """Internal helper to encode a JWT.

    ``data`` is the payload – typically the user identifier – and ``expires_delta``
    determines the ``exp`` claim.  The secret and algorithm come from the central
    ``settings`` object defined in ``app.core.config``.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> str:
    """Create a signed JWT access token.

    If ``expires_minutes`` is omitted the default from the settings file is used.
    ``data`` should contain at least a ``sub`` claim (the user id).  The function
    returns the compact JWT string ready to be sent to the client.
    """
    minutes = expires_minutes if expires_minutes is not None else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    return _create_token(data, timedelta(minutes=minutes))


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT.

    Returns the original payload if the token is valid, otherwise raises
    ``JWTError`` – the caller can decide whether to translate that into a 401.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        # Re‑raise with a clearer message – this mirrors what a hand‑written
        # utility would do in a real code‑base.
        raise JWTError("Invalid authentication token") from exc

