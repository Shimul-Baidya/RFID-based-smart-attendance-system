"""Unit test for student profile validation."""

from app.schemas.student_schema import StudentCreate


def test_student_profile_valid() -> None:
    student = StudentCreate(
        student_number="  371  ",
        registration_number="  202206549  ",
        full_name="  Md. Ahad Siddiki  ",
        department_id=1,
        program_id=1,
        batch=51,
        academic_session="2021-22",
        semester="4-1",
        email="2022ahad@juniv.edu",
    )

    assert student.student_number == "371"
    assert student.registration_number == "202206549"
    assert student.full_name == "Md. Ahad Siddiki"
    assert student.email == "2022ahad@juniv.edu"
    assert student.status == "active"

