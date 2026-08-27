# Attendance Report Filtering and Search

Owner: Zakia Binta Syeed (ZBS)  
Branch: `attendance-report-filtering-by-zakia`
Status: **Scrum 3 complete — Ready for review**

## Current progress

Completed in Scrum 1:

- Reviewed the SRS report requirements.
- Defined and validated the report filters.
- Defined the report response fields.
- Added an initial percentage-calculation prototype.
- Added a repository interface for the shared attendance data.
- Added initial automated tests and API documentation.

Completed in Scrum 2:

- Implemented filtering by department, batch, section, course, and student.
- Implemented inclusive start-date and end-date filtering.
- Connected the repository, service, and controller success workflow.
- Verified attendance totals, percentage, and filtered API responses.
- Added automated tests for repository filtering and the complete API flow.

Completed in Scrum 3:

- Aligned the batch filter with the final `1-100` database constraint.
- Added the shared asynchronous SQLAlchemy database session.
- Implemented the PostgreSQL query for all report filters.
- Added explicit unauthenticated and unauthorized responses.
- Covered invalid, empty, corrected, filtered, and paginated results.
- Added the final shared SQL schema and GitHub Actions quality checks.
- Imported and verified the schema locally on PostgreSQL 17 with 16 tables.
- Executed the report repository against the real PostgreSQL database.

Integration dependency:

- Replace the temporary authentication dependency.
- Shimul's shared authentication implementation must provide the final
  authenticated `ReportUser`; unauthenticated access currently returns 401.

## User story

As a teacher or administrator, I want to filter and search attendance reports
so that I can review the required records efficiently.

## Feature development

Scrum 1 defined the contracts and calculations. Scrum 2 implemented the core
workflow. Scrum 3 connects the final PostgreSQL schema, completes failure-case
coverage, and prepares the feature for pull-request review.

## API contract

`GET /reports/attendance`

Required filters: `department`, `batch`, `section`, `course_id`, `start_date`,
and `end_date`. Optional filters and pagination fields are `student_id`, `page`
(default 1), and `page_size` (default 20, maximum 100).

The response contains student ID/number, name, total classes, present, absent,
late, fractional attendance, percentage, low-attendance status, and the latest
attendance timestamp. An empty search returns HTTP 200 with an empty `items`
list and a clear message.

## Rules and calculations

- `end_date` must be on or after `start_date`.
- Only users with the `teacher` or `admin` role may access the endpoint.
- Effective attendance means the current values in `attendance_records`,
  including approved/manual corrections already applied to those records.
- Earned attendance is the sum of `attendance_value` for all selected classes.
- Percentage is `(earned attendance / total classes) * 100`, rounded to two
  decimal places.
- A student is below the threshold when their percentage is less than 75%.
- Results are ordered by student number and paginated after aggregation.

## Shared schema mapping

- Department: `departments` joined through `students.department_id`.
- Batch: `students.batch` and `course_offerings.batch`.
- Section/course: `course_offerings.section` and `course_offerings.course_id`.
- Date range: `attendance_sessions.scheduled_start`.
- Student identity: `students.id`, `student_number`, and `full_name`.
- Attendance: `attendance_records.status`, `attendance_value`, `recorded_at`,
  and `modified_at`.

The repository must join `attendance_records -> attendance_sessions ->
course_offerings -> students -> departments`, apply all filters before
aggregation, and return the latest corrected record values.

## Dependencies

- Shimul: replace `get_current_report_user` with the shared current-user
  dependency.
- The final schema stores each session's `late_attendance_value`; the report
  intentionally trusts the resulting `attendance_value` on each record.
- The current low-attendance threshold is 75% and can later be moved to shared
  configuration if the team changes the rule.

## PostgreSQL setup

Copy `.env.example` to `.env`, replace the password locally, and import the
schema into a new empty `rfid_attendance` database:

```powershell
psql -U postgres -d rfid_attendance -f database/database_schema.sql
```

Never commit `.env`, database passwords, or local database files.

## Run tests

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/test_reports.py -v
ruff check .
mypy app
sphinx-build -W -b html docs docs/_build/html
```

## Run API documentation

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs` or ReDoc at
`http://127.0.0.1:8000/redoc`.
