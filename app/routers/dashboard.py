from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.dependencies import require_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

ROLE_PERMISSIONS = {
    "admin": [
        "manage_users",
        "manage_departments",
        "manage_courses",
        "view_all_attendance",
        "generate_reports",
        "manage_rfid_cards",
        "view_audit_logs",
    ],
    "teacher": [
        "manage_own_courses",
        "open_attendance_sessions",
        "view_course_attendance",
        "review_correction_requests",
        "generate_reports",
    ],
    "staff": [
        "assign_rfid_cards",
        "manage_students",
        "manage_enrollments",
        "view_attendance_records",
    ],
    "student": [
        "view_own_attendance",
        "submit_correction_request",
    ],
}

@router.get("/admin", response_model=DashboardResponse)
def admin_dashboard(
    current_user: User = Depends(require_role(["admin"]))
):
    return DashboardResponse(
        role=current_user.role,
        message=f"Welcome, {current_user.username}",
        permissions=ROLE_PERMISSIONS["admin"],
    )

@router.get("/teacher", response_model=DashboardResponse)
def teacher_dashboard(
    current_user: User = Depends(require_role(["teacher"]))
):
    return DashboardResponse(
        role=current_user.role,
        message=f"Welcome, {current_user.username}",
        permissions=ROLE_PERMISSIONS["teacher"],
    )

@router.get("/staff", response_model=DashboardResponse)
def staff_dashboard(
    current_user: User = Depends(require_role(["staff"]))
):
    return DashboardResponse(
        role=current_user.role,
        message=f"Welcome, {current_user.username}",
        permissions=ROLE_PERMISSIONS["staff"],
    )

@router.get("/student", response_model=DashboardResponse)
def student_dashboard(
    current_user: User = Depends(require_role(["student"]))
):
    return DashboardResponse(
        role=current_user.role,
        message=f"Welcome, {current_user.username}",
        permissions=ROLE_PERMISSIONS["student"],
    )

