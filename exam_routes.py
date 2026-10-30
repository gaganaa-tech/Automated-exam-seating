from flask import Blueprint, jsonify, request

from backend.database.connection import execute, fetch_all, fetch_one
from backend.middleware.auth_middleware import login_required, role_required

bp = Blueprint("exam_routes", __name__)


@bp.route("/api/exams", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER", "STUDENT")
def list_exams():
    return jsonify({"success": True, "exams": fetch_all("SELECT e.*, s.name AS subject_name FROM exams e LEFT JOIN subjects s ON s.id = e.subject_id ORDER BY e.date_value DESC")})


@bp.route("/api/exams", methods=["POST"])
@login_required
@role_required("ADMIN")
def create_exam():
    payload = request.get_json(silent=True) or {}
    required = ["name", "exam_code", "subject_id", "date_value", "start_time", "end_time"]
    if not all(payload.get(field) not in (None, "") for field in required):
        return jsonify({"success": False, "message": "Incomplete exam details."}), 400
    exam_id = execute(
        "INSERT INTO exams (name, exam_code, subject_id, date_value, start_time, end_time, duration_minutes, student_count, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
        (
            payload["name"],
            payload["exam_code"],
            payload["subject_id"],
            payload["date_value"],
            payload["start_time"],
            payload["end_time"],
            payload.get("duration_minutes", 120),
            payload.get("student_count", 0),
            payload.get("status", "Upcoming"),
        ),
    )
    return jsonify({"success": True, "message": "Exam created successfully.", "id": exam_id})


@bp.route("/api/exams/<int:exam_id>", methods=["PUT"])
@login_required
@role_required("ADMIN")
def update_exam(exam_id):
    payload = request.get_json(silent=True) or {}
    execute(
        "UPDATE exams SET name = %s, exam_code = %s, subject_id = %s, date_value = %s, start_time = %s, end_time = %s, duration_minutes = %s, student_count = %s, status = %s, updated_at = NOW() WHERE id = %s",
        (
            payload.get("name"),
            payload.get("exam_code"),
            payload.get("subject_id"),
            payload.get("date_value"),
            payload.get("start_time"),
            payload.get("end_time"),
            payload.get("duration_minutes", 120),
            payload.get("student_count", 0),
            payload.get("status", "Upcoming"),
            exam_id,
        ),
    )
    return jsonify({"success": True, "message": "Exam updated successfully."})


@bp.route("/api/exams/<int:exam_id>", methods=["DELETE"])
@login_required
@role_required("ADMIN")
def delete_exam(exam_id):
    execute("DELETE FROM exams WHERE id = %s", (exam_id,))
    return jsonify({"success": True, "message": "Exam deleted successfully."})
