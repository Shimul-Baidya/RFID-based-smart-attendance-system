from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.security import get_password_hash

def setup_test_user(db_session: Session, username: str = "apiuser", password: str = "apipassword"):
    user = User(
        id=10,
        username=username,
        email=f"{username}@example.com",
        password_hash=get_password_hash(password),
        role="student",
        status="active"
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_login_for_access_token_success(client: TestClient, db_session: Session):
    setup_test_user(db_session, "teststudent", "securepassword")

    response = client.post(
        "/token",
        data={"username": "teststudent", "password": "securepassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_for_access_token_wrong_password(client: TestClient, db_session: Session):
    setup_test_user(db_session, "teststudent", "securepassword")

    response = client.post(
        "/token",
        data={"username": "teststudent", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_for_access_token_nonexistent_user(client: TestClient, db_session: Session):
    response = client.post(
        "/token",
        data={"username": "ghostuser", "password": "anypassword"}
    )
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_read_users_me_success(client: TestClient, db_session: Session):
    # First login to get a token
    setup_test_user(db_session, "teststudent", "securepassword")
    login_response = client.post(
        "/token",
        data={"username": "teststudent", "password": "securepassword"}
    )
    token = login_response.json()["access_token"]

    # Now use the token to access the protected route
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "teststudent"
    assert data["role"] == "student"
    assert data["email"] == "teststudent@example.com"

def test_read_users_me_unauthorized(client: TestClient):
    # Access without providing a token
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_read_users_me_invalid_token(client: TestClient):
    # Access with a fake token
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer fake.invalid.token"}
    )
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

