from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

admin_portal_bp = Blueprint("admin_portal_bp", __name__, url_prefix="/admin")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@admin_portal_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if session.get("role") != "admin": return api_response("error", message="Unauthorized.", http_status=401)

    counts = db.session.execute(
        text("""
            SELECT 
                COUNT(CASE WHEN role = 'farmer' THEN 1 END) as farmers,
                COUNT(CASE WHEN role = 'buyer' THEN 1 END) as buyers,
                COUNT(CASE WHEN role = 'driver' THEN 1 END) as drivers,
                COUNT(CASE WHEN approval_status = 'pending' THEN 1 END) as pending
            FROM users
        """)
    ).mappings().first()

    return api_response("success", data=dict(counts))

@admin_portal_bp.route("/verify-user/<int:user_id>", methods=["PATCH"])
def verify_user(user_id):
    if session.get("role") != "admin": return api_response("error", message="Unauthorized.", http_status=401)

    payload = request.get_json(silent=True) or {}
    status = payload.get("status", "approved")

    db.session.execute(text("UPDATE users SET approval_status = :status WHERE id = :uid"), {"status": status, "uid": user_id})
    db.session.commit()
    return api_response("success", message=f"User approval status updated to {status}.")
