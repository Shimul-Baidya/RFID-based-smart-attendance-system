import jwt
from datetime import datetime, timezone, timedelta
from app.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

def test_password_hashing():
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    
    assert password != hashed
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data=data)
    
    # Verify the token can be decoded
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload.get("sub") == "testuser"
    assert "exp" in payload

def test_create_access_token_with_custom_expiry():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data=data, expires_delta=expires_delta)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Expiry time should be roughly 5 minutes from now
    exp_timestamp = payload.get("exp")
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    time_difference = exp_datetime - now
    # Check if the difference is roughly 5 minutes (allowing a few seconds margin of error)
    assert 4 < time_difference.total_seconds() / 60 <= 5

