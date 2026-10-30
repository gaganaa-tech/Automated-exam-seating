from flask import Blueprint, jsonify

from backend.database.connection import fetch_all
from backend.middleware.auth_middleware import login_required, role_required
from backend.services.auth_service import get_dashboard_stats

bp = Blueprint("dashboard_routes", __name__)


@bp.route("/api/dashboard", methods=["GET"])
@login_required
def dashboard():
    stats = get_dashboard_stats()
    recent_exams = fetch_all(
        "SELECT name, exam_code, date_value FROM exams ORDER BY created_at DESC LIMIT 5"
    )
    for exam in recent_exams:
        if hasattr(exam["date_value"], "isoformat"):
            exam["date_value"] = exam["date_value"].isoformat()
    recent_activity = fetch_all("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 8")
    return jsonify({"success": True, "stats": stats, "recent_exams": recent_exams, "recent_activity": recent_activity})


@bp.route("/api/dashboard/admin", methods=["GET"])
@login_required
@role_required("ADMIN")
def admin_dashboard():
    return dashboard()
