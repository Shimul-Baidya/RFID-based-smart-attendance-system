from fastapi import FastAPI

app = FastAPI(
    title="RFID Attendance System API",
    description="Backend API for the RFID-Based Smart Attendance System",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the RFID Attendance System API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
