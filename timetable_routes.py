from flask import Blueprint, jsonify, request

from backend.database.connection import execute, fetch_all
from backend.middleware.auth_middleware import login_required, role_required

bp = Blueprint("timetable_routes", __name__)


@bp.route("/api/timetable", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER")
def get_timetable():
    return jsonify({"success": True, "timetable": fetch_all("SELECT * FROM timetable ORDER BY exam_date DESC")})


@bp.route("/api/timetable", methods=["POST"])
@login_required
@role_required("ADMIN")
def create_timetable():
    payload = request.get_json(silent=True) or {}
    execute(
        "INSERT INTO timetable (exam_id, room_id, invigilator_id, exam_date, start_time, end_time, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())",
        (payload.get("exam_id"), payload.get("room_id"), payload.get("invigilator_id"), payload.get("exam_date"), payload.get("start_time"), payload.get("end_time")),
    )
    return jsonify({"success": True, "message": "Timetable entry created successfully."})
