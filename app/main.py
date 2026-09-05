"""Create and configure the FastAPI application."""

from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends

from app.database import get_db
from app.routers import dashboard_router
from app.routers import auth, users
from app.routers.attendance_router import router as attendance_router

app = FastAPI(
    title="RFID Attendance System API",
    description="Backend API for the RFID-Based Smart Attendance System",
    version="1.0.0",
)

app.include_router(dashboard_router.router)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance_router)
DatabaseSession = Annotated[Session, Depends(get_db)]

@app.get("/")
def read_root() -> dict[str, str]:
    """Return the API welcome message.

    Returns:
        A welcome message for the attendance-system API.
    """
    return {"message": "Welcome to the RFID Attendance System API"}


@app.get("/health")
def health_check(
    database: DatabaseSession,
) -> dict[str, str]:
    """Return the application and database health status.

    Args:
        database: Active SQLAlchemy database session.

    Returns:
        Current API and database connection status.
    """
    try:
        database.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
        }
    except SQLAlchemyError as error:
        return {
            "status": "error",
            "database": "disconnected",
            "details": str(error),
        }
