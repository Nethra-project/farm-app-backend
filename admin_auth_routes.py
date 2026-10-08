import secrets
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from database import db

admin_auth_bp = Blueprint("admin_auth_bp", __name__, url_prefix="/admin/auth")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@admin_auth_bp.route("/seed-super-admin", methods=["POST"])
def seed_admin():
    existing = db.session.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1")).first()
    if existing: return api_response("error", message="Admin already exists.", http_status=400)

    payload = request.get_json(silent=True) or {}
    email = payload.get("email", "admin@platform.com")
    pwd_hash = generate_password_hash(payload.get("password", "SuperAdminPass123!"))

    res = db.session.execute(
        text("INSERT INTO users (phone, email, password_hash, role, approval_status) VALUES ('0000000000', :email, :pwd, 'admin', 'approved')"),
        {"email": email, "pwd": pwd_hash}
    )
    db.session.commit()
    return api_response("success", data={"admin_id": res.lastrowid}, message="Super Admin created.")

@admin_auth_bp.route("/login", methods=["POST"])
def admin_login():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    password = payload.get("password")

    admin = db.session.execute(text("SELECT * FROM users WHERE email = :email AND role = 'admin' LIMIT 1"), {"email": email}).mappings().first()
    if not admin or not check_password_hash(admin["password_hash"], password):
        return api_response("error", message="Invalid credentials.", http_status=401)

    session["user_id"] = admin["id"]
    session["role"] = "admin"
    return api_response("success", data={"admin_id": admin["id"]})
