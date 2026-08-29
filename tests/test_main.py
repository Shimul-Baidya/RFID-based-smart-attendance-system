"""Integration tests for the FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test that the application health endpoint is available."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_attendance_scan_route_is_registered() -> None:
    """Test that the attendance scan route appears in OpenAPI."""
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert response.status_code == 200
    assert "/attendance/scan" in paths
    assert "post" in paths["/attendance/scan"]
