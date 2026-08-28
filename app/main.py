"""FastAPI application entry point."""

from fastapi import FastAPI

from app.controllers.student_controller import router as student_router

app = FastAPI(
    title="RFID-Based Smart Attendance System",
    version="0.1.0",
)

app.include_router(student_router)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """Confirm that the API is running."""

    return {"status": "ok"}
