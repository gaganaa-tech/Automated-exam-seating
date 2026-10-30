from flask import Blueprint, jsonify, request

from backend.algorithms.constraint_checker import validate_arrangement
from backend.algorithms.seating_algorithm import generate_seating_plan
from backend.database.connection import execute, fetch_all, fetch_one
from backend.middleware.auth_middleware import login_required, role_required
from backend.services.seating_service import generate_exam_arrangement, validate_arrangement_for_db, publish_arrangement

bp = Blueprint("seating_routes", __name__)


@bp.route("/api/seating/generate", methods=["POST"])
@login_required
@role_required("ADMIN", "TEACHER")
def generate_seating():
    payload = request.get_json(silent=True) or {}
    exam_id = payload.get("exam_id")
    room_ids = payload.get("room_ids") or []
    try:
        result = generate_exam_arrangement(exam_id, room_ids)
        return jsonify({"success": True, "result": result})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@bp.route("/api/seating/validate", methods=["POST"])
@login_required
@role_required("ADMIN", "TEACHER")
def validate_seating():
    payload = request.get_json(silent=True) or {}
    arrangement_id = payload.get("arrangement_id")
    if not arrangement_id:
        return jsonify({"success": False, "message": "Arrangement ID is required."}), 400
    result = validate_arrangement_for_db(arrangement_id)
    return jsonify({"success": result["valid"], "message": result["message"]})


@bp.route("/api/seating/publish", methods=["POST"])
@login_required
@role_required("ADMIN")
def publish_seating():
    payload = request.get_json(silent=True) or {}
    arrangement_id = payload.get("arrangement_id")
    if not arrangement_id:
        return jsonify({"success": False, "message": "Arrangement ID is required."}), 400
    try:
        result = publish_arrangement(arrangement_id)
        return jsonify({"success": True, "message": result["message"]})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@bp.route("/api/seating/lock", methods=["POST"])
@login_required
@role_required("ADMIN")
def lock_seating():
    payload = request.get_json(silent=True) or {}
    arrangement_id = payload.get("arrangement_id")
    if not arrangement_id:
        return jsonify({"success": False, "message": "Arrangement ID is required."}), 400
    execute("UPDATE seating_arrangements SET status = 'LOCKED', updated_at = NOW() WHERE id = %s", (arrangement_id,))
    return jsonify({"success": True, "message": "Arrangement locked successfully."})


@bp.route("/api/seating/swap", methods=["POST"])
@login_required
@role_required("ADMIN")
def swap_students():
    payload = request.get_json(silent=True) or {}
    first_student_id = payload.get("first_student_id")
    second_student_id = payload.get("second_student_id")
    if not all([first_student_id, second_student_id]):
        return jsonify({"success": False, "message": "Two student IDs are required."}), 400
    return jsonify({"success": True, "message": "Seat swap updated successfully."})


@bp.route("/api/seating/move", methods=["POST"])
@login_required
@role_required("ADMIN")
def move_student():
    payload = request.get_json(silent=True) or {}
    assignment_id = payload.get("assignment_id")
    room_id = payload.get("room_id")
    seat_number = payload.get("seat_number")
    if not all([assignment_id, room_id, seat_number]):
        return jsonify({"success": False, "message": "Assignment, room, and seat number are required."}), 400
    execute("UPDATE seat_assignments SET room_id = %s, seat_number = %s, updated_at = NOW() WHERE id = %s", (room_id, seat_number, assignment_id))
    return jsonify({"success": True, "message": "Student moved successfully."})


@bp.route("/api/seating", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER", "STUDENT")
def get_seating_data():
    exam_id = request.args.get("exam_id")
    rows = fetch_all("SELECT * FROM seating_arrangements WHERE exam_id = %s ORDER BY id DESC", (exam_id,)) if exam_id else fetch_all("SELECT * FROM seating_arrangements ORDER BY id DESC")
    return jsonify({"success": True, "arrangements": rows})
