from fastapi import FastAPI

from app.routers import dashboard_router

app = FastAPI(
    title="RFID-Based Smart Attendance System",
    version="0.1.0",
)

app.include_router(dashboard_router.router)


@app.get("/")
def root():
    return {"message": "RFID Smart Attendance System API is running"}