from flask import Blueprint, jsonify, request

from backend.database.connection import execute, fetch_all, fetch_one
from backend.middleware.auth_middleware import login_required, role_required
from backend.services.attendance_service import get_attendance_rows, mark_attendance

bp = Blueprint("attendance_routes", __name__)


@bp.route("/api/attendance", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER")
def list_attendance():
    exam_id = request.args.get("exam_id")
    rows = get_attendance_rows(exam_id) if exam_id else get_attendance_rows()
    return jsonify({"success": True, "attendance": rows})


@bp.route("/api/attendance", methods=["POST"])
@login_required
@role_required("ADMIN", "TEACHER")
def create_attendance():
    payload = request.get_json(silent=True) or {}
    student_id = payload.get("student_id")
    exam_id = payload.get("exam_id")
    present_status = payload.get("present_status")
    if not all([student_id, exam_id, present_status is not None]):
        return jsonify({"success": False, "message": "Student, exam and attendance status are required."}), 400
    mark_attendance(student_id, exam_id, int(present_status))
    return jsonify({"success": True, "message": "Attendance updated successfully."})
