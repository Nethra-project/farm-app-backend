from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db

buyer_auth_bp = Blueprint("buyer_auth_bp", __name__, url_prefix="/buyer/auth")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@buyer_auth_bp.route("/signup", methods=["POST"])
def buyer_signup():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()
    buyer_type = payload.get("buyer_type", "consumer")

    if not phone or not password:
        return api_response("error", message="Phone and password are required.", http_status=400)

    pwd_hash = generate_password_hash(password)
    approval_status = "pending" if buyer_type == "bulk_buyer" else "approved"

    try:
        res = db.session.execute(
            text("INSERT INTO users (phone, password_hash, role, approval_status) VALUES (:phone, :pwd, 'buyer', :app)"),
            {"phone": phone, "pwd": pwd_hash, "app": approval_status}
        )
        user_id = res.lastrowid

        db.session.execute(
            text("""
                INSERT INTO buyer_profiles (user_id, buyer_type, full_name_or_contact, business_name, gstin)
                VALUES (:uid, :btype, :name, :bname, :gst)
            """),
            {
                "uid": user_id, "btype": buyer_type, "name": payload.get("full_name", "Buyer"),
                "bname": payload.get("business_name"), "gst": payload.get("gstin")
            }
        )
        db.session.commit()
        return api_response("success", data={"user_id": user_id, "approval_status": approval_status}, message="Buyer registered.", http_status=201)
    except SQLAlchemyError:
        db.session.rollback()
        return api_response("error", message="Phone number already registered.", http_status=400)

@buyer_auth_bp.route("/login", methods=["POST"])
def buyer_login():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()

    user = db.session.execute(
        text("SELECT * FROM users WHERE phone = :phone AND role = 'buyer' LIMIT 1"),
        {"phone": phone}
    ).mappings().first()

    if not user or not check_password_hash(user["password_hash"], password):
        return api_response("error", message="Invalid buyer credentials.", http_status=401)

    session["user_id"] = user["id"]
    session["role"] = "buyer"

    return api_response("success", data={"user_id": user["id"], "approval_status": user["approval_status"]})
