# RFID-based-smart-attendance-system

## Local PostgreSQL setup

The final team database schema requires PostgreSQL 14 or later. Create an empty
database, copy `.env.example` to `.env`, set the local password, and import:

```powershell
psql -U postgres -d rfid_attendance -f database/database_schema.sql
```

Install and verify the application:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Keep `.env` private. Do not commit passwords or local database files.
