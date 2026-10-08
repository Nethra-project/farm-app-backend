from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()
    role = payload.get("role", "farmer").lower()

    if not phone or not password or role not in ['farmer', 'fpo']:
        return api_response("error", message="Phone, password, and valid role (farmer/fpo) are required.", http_status=400)

    pwd_hash = generate_password_hash(password)

    try:
        res = db.session.execute(
            text("INSERT INTO users (phone, password_hash, role, approval_status) VALUES (:phone, :pwd, :role, 'approved')"),
            {"phone": phone, "pwd": pwd_hash, "role": role}
        )
        db.session.commit()
        return api_response("success", data={"user_id": res.lastrowid, "role": role}, message="Registration successful.", http_status=201)
    except SQLAlchemyError:
        db.session.rollback()
        return api_response("error", message="Phone number already registered.", http_status=400)

@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()

    user = db.session.execute(
        text("SELECT * FROM users WHERE phone = :phone LIMIT 1"),
        {"phone": phone}
    ).mappings().first()

    if not user or not check_password_hash(user["password_hash"], password):
        return api_response("error", message="Invalid phone or password.", http_status=401)

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    return api_response("success", data={"user_id": user["id"], "role": user["role"]}, message="Login successful.")
