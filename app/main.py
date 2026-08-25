"""FastAPI application entry point for the smart attendance system."""

from fastapi import FastAPI

from app.controllers.report_controller import router as report_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """

    application = FastAPI(
        title="RFID-Based Smart Attendance System",
        description="API for RFID attendance management and reporting.",
        version="0.1.0",
    )
    application.include_router(report_router)
    return application


app = create_app()
