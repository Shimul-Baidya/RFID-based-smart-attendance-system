from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from app.database import get_db

app = FastAPI(
    title="RFID Attendance System API",
    description="Backend API for the RFID-Based Smart Attendance System",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the RFID Attendance System API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "details": str(e)}
