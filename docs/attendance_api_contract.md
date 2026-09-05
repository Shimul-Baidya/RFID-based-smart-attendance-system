# Simulated RFID Attendance API Contract

## Feature Owner

Joyoshree Saha

## Source Requirements

- SRS Section 3.1.2: Marking Attendance with an RFID Card
- SRS Section 3.2.1: Attendance response time
- SRS Section 3.2.4: Duplicate attendance prevention
- SRS Section 3.2.5: Attendance business rules

## User Story

As a student, I want to tap my RFID card so that my attendance is recorded automatically for the current class.

## Confirmed RFID Interface

The following interface was agreed with Ahad:

- Student model: `app/models/student_model.py`
- Student primary key: `Student.id`
- RFID model: `app/models/rfid_model.py`
- RFID UID field: `RFIDCard.uid`
- RFID active condition: `RFIDCard.status == "active"`
- Relationship: `RFIDCard.student_id -> Student.id`
- A student may have historical RFID cards, but only one card may be active.
- Unknown or inactive RFID cards return no student.
- Course IDs are three-digit integers, for example `401` and `412`.

Proposed lookup interface:

```python
async def find_student_by_rfid_uid(
    session,
    uid: str,
) -> Student | None:
    ...
```

## Attendance Validation Rules

The attendance service shall validate the scan in this order:

1. Validate that the request contains an RFID UID and session ID.
2. Normalize the RFID UID.
3. Find the student associated with an active RFID card.
4. Reject an unknown or inactive RFID card.
5. Find the requested attendance session.
6. Confirm that the attendance session is open.
7. Confirm that the current time is within the attendance window.
8. Confirm that the student is eligible for the class or course.
9. Check whether attendance already exists for the student and session.
10. Create only one attendance record.
11. Return a clear success or rejection response.

## Proposed Endpoint

```http
POST /attendance/simulated-scan
```

## Proposed Request

```json
{
  "rfid_uid": "04-A1-B2-C3-D4",
  "session_id": 101
}
```

## Request Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `rfid_uid` | string | Yes | UID received from the simulated RFID reader |
| `session_id` | integer | Yes | Attendance session for the current class |

## Successful Response

HTTP status:

```text
201 Created
```

Example:

```json
{
  "message": "Attendance recorded successfully",
  "attendance_id": 501,
  "student_id": 25,
  "session_id": 101,
  "course_id": 401,
  "status": "present",
  "duplicate": false,
  "recorded_at": "2026-08-25T21:30:00+06:00"
}
```

## Duplicate Scan Response

A duplicate scan shall not create another database record.

HTTP status:

```text
200 OK
```

Example:

```json
{
  "message": "Attendance was already recorded",
  "attendance_id": 501,
  "student_id": 25,
  "session_id": 101,
  "course_id": 401,
  "status": "present",
  "duplicate": true,
  "recorded_at": "2026-08-25T21:30:00+06:00"
}
```

## Rejection Responses

### Unknown or Inactive RFID

HTTP status:

```text
404 Not Found
```

```json
{
  "detail": "Active RFID card was not found"
}
```

### Attendance Session Not Found

HTTP status:

```text
404 Not Found
```

```json
{
  "detail": "Attendance session was not found"
}
```

### Attendance Session Closed

HTTP status:

```text
409 Conflict
```

```json
{
  "detail": "Attendance session is not open"
}
```

### Outside Attendance Window

HTTP status:

```text
409 Conflict
```

```json
{
  "detail": "Attendance cannot be recorded outside the allowed time window"
}
```

### Student Not Eligible

HTTP status:

```text
403 Forbidden
```

```json
{
  "detail": "Student is not eligible for this attendance session"
}
```

## Duplicate Prevention

Attendance must be unique for:

```text
student_id + session_id
```

Duplicate prevention shall be implemented at both levels:

1. Service-level existing-attendance check.
2. PostgreSQL unique constraint on `student_id` and `session_id`.

## Initial Required Tests

- A registered active RFID records attendance.
- An unknown RFID is rejected.
- An inactive RFID is rejected.
- A missing attendance session is rejected.
- A closed attendance session is rejected.
- A scan outside the allowed time window is rejected.
- An ineligible student is rejected.
- A repeated scan does not create another record.
- The correct student, session, course, date, time and status are stored.
- A stored `course_id` follows the agreed three-digit format, such as `401` or `412`.

## Open Questions for Scrum Meeting

1. What fields will identify the attendance session and course?
2. Who owns the `AttendanceSession` model?
3. Will `session_id` be an integer or UUID?
4. What fields indicate that a session is open?
5. How are `starts_at` and `ends_at` stored?
6. Which timezone will the project use?
7. Should a duplicate scan return `200 OK` or `409 Conflict`?
8. What is the agreed common error-response format?

## Current Git Information

- Base branch: `main`
- Feature branch: `attendance-by-joyoshree`
- Planned endpoint: `POST /attendance/simulated-scan`

## Document Status

This is a proposed Sprint 1 contract. Attendance-session fields, timezone handling and common error formatting must be confirmed during the Scrum meeting before final implementation.
