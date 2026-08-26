Attendance Report Filtering
===========================

User Story
----------

As a teacher or administrator, I want to filter and search attendance reports
so that I can review required records efficiently.

Endpoint
--------

``GET /reports/attendance`` accepts department, batch, section, course, student,
date-range, and pagination filters. Only teachers and administrators are
authorized to retrieve reports.

Calculation
-----------

Attendance percentage is the sum of effective ``attendance_value`` values
divided by the total number of selected classes, multiplied by 100. The stored
effective values ensure approved corrections and fractional attendance are
included.

The complete design, schema mapping, and dependency notes are available in
``attendance_report_design.md``.

Scrum 2 Increment
-----------------

The core successful workflow now filters effective attendance rows by
department, batch, section, course, optional student, and inclusive date range.
The service then groups the matching rows and returns paginated summaries.
