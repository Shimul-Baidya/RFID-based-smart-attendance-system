from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth import authenticate_user
from app.services.security import get_password_hash

def test_authenticate_user_success(db_session: Session):
    # Setup: Create a test user in the database
    password = "correctpassword"
    hashed = get_password_hash(password)
    test_user = User(
        id=1,
        username="teststudent",
        email="teststudent@example.com",
        password_hash=hashed,
        role="student"
    )
    db_session.add(test_user)
    db_session.commit()

    # Action: Attempt authentication
    authenticated_user = authenticate_user(db_session, "teststudent", password)
    
    # Assert: Authentication succeeds and returns the user
    assert authenticated_user is not False
    assert authenticated_user.username == "teststudent"
    assert authenticated_user.role == "student"

def test_authenticate_user_wrong_password(db_session: Session):
    password = "correctpassword"
    hashed = get_password_hash(password)
    test_user = User(
        id=2,
        username="teststudent",
        email="teststudent@example.com",
        password_hash=hashed,
        role="student"
    )
    db_session.add(test_user)
    db_session.commit()

    # Attempt authentication with wrong password
    authenticated_user = authenticate_user(db_session, "teststudent", "wrongpassword")
    
    assert authenticated_user is False

def test_authenticate_user_nonexistent_user(db_session: Session):
    # Attempt authentication for a user that does not exist in the database
    authenticated_user = authenticate_user(db_session, "ghostuser", "anypassword")
    
    assert authenticated_user is False
