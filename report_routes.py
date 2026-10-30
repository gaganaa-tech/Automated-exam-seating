from flask import Blueprint, jsonify, request

from backend.database.connection import fetch_all
from backend.middleware.auth_middleware import login_required, role_required
from backend.services.report_service import get_reports

bp = Blueprint("report_routes", __name__)


@bp.route("/api/reports", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER")
def reports():
    return jsonify({"success": True, "reports": get_reports()})


@bp.route("/api/reports/export", methods=["GET"])
@login_required
@role_required("ADMIN", "TEACHER")
def export_reports():
    rows = fetch_all("SELECT * FROM students")
    return jsonify({"success": True, "data": rows})
