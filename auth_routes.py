from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    phone = data.get('phone')
    if not phone or len(phone) < 10:
        return jsonify({"status": "error", "message": "Invalid phone number."}), 400

    otp_code = "123456"
    expires_at = datetime.now() + timedelta(minutes=15)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO otp_codes (phone, otp_code, expires_at) VALUES (?, ?, ?)", (phone, otp_code, expires_at))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": f"OTP sent to {phone}. (Code: {otp_code})"}), 200

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    phone = data.get('phone')
    otp_code = data.get('otp_code')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM otp_codes WHERE phone = ? AND otp_code = ? AND is_verified = 0 ORDER BY id DESC LIMIT 1", (phone, otp_code))
    record = cursor.fetchone()

    if not record:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Invalid or expired OTP."}), 400

    cursor.execute("UPDATE otp_codes SET is_verified = 1 WHERE id = ?", (record['id'],))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Mobile number verified."}), 200

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role')

    if not phone or not password or not role:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM otp_codes WHERE phone = ? AND is_verified = 1", (phone,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Mobile number not verified by server OTP."}), 403

    approval_status = 'verified' if role == 'consumer' else 'pending'
    password_hash = generate_password_hash(password)

    try:
        cursor.execute("INSERT INTO users (phone, password_hash, role, approval_status) VALUES (?, ?, ?, ?)", (phone, password_hash, role, approval_status))
        user_id = cursor.lastrowid

        if role == 'farmer':
            cursor.execute("""
                INSERT INTO farmer_profiles (user_id, full_name, village, district, state, pincode, crops_grown, payment_details, fpo_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, data.get('full_name'), data.get('village'), data.get('district'), data.get('state'), data.get('pincode'), data.get('crops_grown'), data.get('payment_details'), data.get('fpo_name')))
        elif role == 'fpo':
            cursor.execute("""
                INSERT INTO fpo_profiles (user_id, fpo_name, registration_type, registration_number, registration_year, contact_person_name, designation, office_address, district, state, pincode, member_farmer_count, crops_handled, bank_account_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, data.get('fpo_name'), data.get('registration_type'), data.get('registration_number'), data.get('registration_year'), data.get('contact_person_name'), data.get('designation'), data.get('office_address'), data.get('district'), data.get('state'), data.get('pincode'), data.get('member_farmer_count', 0), data.get('crops_handled'), data.get('bank_account_details')))
        elif role in ['consumer', 'bulk_buyer']:
            cursor.execute("""
                INSERT INTO buyer_profiles (user_id, buyer_type, full_name_or_contact, business_name, gstin, delivery_address, city, pincode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, role, data.get('full_name_or_contact'), data.get('business_name'), data.get('gstin'), data.get('delivery_address'), data.get('city'), data.get('pincode')))
        elif role == 'driver':
            cursor.execute("""
                INSERT INTO driver_profiles (user_id, full_name, city, pincodes_served, vehicle_type, vehicle_number, load_capacity_kg, payout_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, data.get('full_name'), data.get('city'), data.get('pincodes_served'), data.get('vehicle_type'), data.get('vehicle_number'), data.get('load_capacity_kg'), data.get('payout_details')))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Registration successful.", "user_id": user_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    phone = data.get('phone')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"status": "error", "message": "Invalid phone or password."}), 401

    if user['approval_status'] == 'blocked':
        return jsonify({"status": "error", "message": "Account is blocked."}), 403

    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={"role": user['role'], "approval_status": user['approval_status']}
    )

    return jsonify({
        "status": "success",
        "token": access_token,
        "user": {
            "id": user['id'],
            "role": user['role'],
            "approval_status": user['approval_status']
        }
    }), 200
