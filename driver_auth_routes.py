from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db

driver_auth_bp = Blueprint("driver_auth_bp", __name__, url_prefix="/driver/auth")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@driver_auth_bp.route("/signup", methods=["POST"])
def driver_signup():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()
    full_name = str(payload.get("full_name", "")).strip()
    vehicle_number = str(payload.get("vehicle_number", "")).strip().upper()

    if not phone or not password or not full_name or not vehicle_number:
        return api_response("error", message="Missing required driver registration fields.", http_status=400)

    pwd_hash = generate_password_hash(password)

    try:
        user_res = db.session.execute(
            text("INSERT INTO users (phone, password_hash, role, approval_status) VALUES (:phone, :pwd, 'driver', 'pending')"),
            {"phone": phone, "pwd": pwd_hash}
        )
        user_id = user_res.lastrowid

        db.session.execute(
            text("""
                INSERT INTO driver_profiles (user_id, full_name, city, district, pincodes_served, vehicle_type, vehicle_number, load_capacity_kg)
                VALUES (:uid, :name, :city, :district, :pincodes, :vtype, :vnum, :cap)
            """),
            {
                "uid": user_id, "name": full_name, "city": payload.get("city", ""),
                "district": payload.get("district", ""), "pincodes": payload.get("pincodes_served", ""),
                "vtype": payload.get("vehicle_type", "tempo"), "vnum": vehicle_number, "cap": payload.get("load_capacity_kg", 500)
            }
        )
        db.session.commit()
        return api_response("success", data={"user_id": user_id, "approval_status": "pending"}, message="Driver registered pending approval.", http_status=201)
    except SQLAlchemyError:
        db.session.rollback()
        return api_response("error", message="Phone or vehicle number already registered.", http_status=400)

@driver_auth_bp.route("/login", methods=["POST"])
def driver_login():
    payload = request.get_json(silent=True) or {}
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", "")).strip()

    driver = db.session.execute(
        text("SELECT u.id, u.password_hash, u.approval_status FROM users u WHERE u.phone = :phone AND u.role = 'driver' LIMIT 1"),
        {"phone": phone}
    ).mappings().first()

    if not driver or not check_password_hash(driver["password_hash"], password):
        return api_response("error", message="Invalid credentials.", http_status=401)

    session["user_id"] = driver["id"]
    session["role"] = "driver"
    session["approval_status"] = driver["approval_status"]

    return api_response("success", data={"user_id": driver["id"], "approval_status": driver["approval_status"]})
