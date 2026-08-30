"""Integration tests for the FastAPI application."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app


def test_health_endpoint() -> None:
    """Test the application and database health endpoint."""
    database = MagicMock(spec=Session)

    def override_database() -> MagicMock:
        """Return a mocked database session."""
        return database

    app.dependency_overrides[get_db] = override_database

    try:
        with TestClient(app) as client:
            response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }
    database.execute.assert_called_once()


def test_attendance_scan_route_is_registered() -> None:
    """Test that the attendance scan route appears in OpenAPI."""
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    paths = response.json()["paths"]

    assert response.status_code == 200
    assert "/attendance/scan" in paths
    assert "post" in paths["/attendance/scan"]