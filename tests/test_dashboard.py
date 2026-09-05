from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_admin_receives_dashboard():
    """Verify that an admin receives a successful dashboard response."""
    response = client.get(
        "/dashboard/",
        params={
            "user_name": "Arpita",
            "user_role": "admin",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_student_receives_dashboard():
    """Verify that a student receives the appropriate dashboard actions."""
    response = client.get(
        "/dashboard/",
        params={
            "user_name": "Rakib",
            "user_role": "student",
        },
    )

    assert response.status_code == 200
    assert "view_attendance" in response.json()["allowed_actions"]


def test_invalid_role_is_rejected():
    """Verify that an invalid role is rejected with 403 Forbidden."""
    response = client.get(
        "/dashboard/",
        params={
            "user_name": "X",
            "user_role": "hacker",
        },
    )

    assert response.status_code == 403


def test_missing_credentials_is_unauthenticated():
    """Verify that missing credentials return 401 Unauthorized."""
    response = client.get("/dashboard/")

    assert response.status_code == 401