"""Create and configure the FastAPI application."""

from fastapi import FastAPI

from app.routers.attendance_router import router as attendance_router

app = FastAPI(
    title="RFID-Based Smart Attendance System",
    version="1.0.0",
)

app.include_router(attendance_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Return the current API health status.

    Returns:
        A message confirming that the API is running.
    """
    return {"status": "healthy"}
