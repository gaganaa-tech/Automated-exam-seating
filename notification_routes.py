from flask import Blueprint, jsonify, request

from backend.database.connection import fetch_all
from backend.middleware.auth_middleware import login_required
from backend.services.notification_service import create_notification, get_notifications, unread_count

bp = Blueprint("notification_routes", __name__)


@bp.route("/api/notifications", methods=["GET"])
@login_required
def list_notifications():
    user = request.args.get("user_id")
    return jsonify({"success": True, "notifications": get_notifications(user), "unread_count": unread_count(user)})


@bp.route("/api/notifications", methods=["POST"])
@login_required
def create_notification_route():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    title = payload.get("title")
    message = payload.get("message")
    if not all([user_id, title, message]):
        return jsonify({"success": False, "message": "User, title and message are required."}), 400
    create_notification(user_id, title, message)
    return jsonify({"success": True, "message": "Notification created successfully."})
