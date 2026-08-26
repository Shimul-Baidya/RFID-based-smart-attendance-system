# Attendance Report Filtering and Search

Owner: Zakia Binta Syeed (ZBS)  
Branch: `attendance-report-filtering-by-zakia`
Status: **In Progress — Scrum 2 core workflow**

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

Still in progress:

- Connect the shared PostgreSQL database session and models.
- Replace the temporary in-memory repository with PostgreSQL queries.
- Replace the temporary authentication dependency.
- Confirm the late-attendance value and attendance threshold with the team.
- Run integration tests using shared attendance records.
- Complete review and integration in the later Scrum cycles.

## User story

As a teacher or administrator, I want to filter and search attendance reports
so that I can review the required records efficiently.

## Sprint 1 goal

Define the API contract, validation rules, response fields, an initial
calculation prototype, the data-access boundary, and initial automated tests.
The concrete database and shared authentication adapters will be connected
after the owning teammates merge those dependencies.

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
- Batch: `students.batch_year` and `course_offerings.batch_year`.
- Section/course: `course_offerings.section` and `course_offerings.course_id`.
- Date range: `attendance_sessions.scheduled_start`.
- Student identity: `students.id`, `student_number`, and `full_name`.
- Attendance: `attendance_records.status`, `attendance_value`, `recorded_at`,
  and `modified_at`.

The repository must join `attendance_records -> attendance_sessions ->
course_offerings -> students -> departments`, apply all filters before
aggregation, and return the latest corrected record values.

## Dependencies and blockers

- Shimul: replace `get_current_report_user` with the shared current-user
  dependency.
- Jemima/team database owner: implement `AttendanceReportRepository` using the
  shared database session and attendance models.
- Team decision: confirm whether late attendance earns 0.5 or another value.
  This feature intentionally trusts the stored `attendance_value`.
- Team decision: confirm whether the low-attendance threshold is globally 75%
  or configured per course.

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
