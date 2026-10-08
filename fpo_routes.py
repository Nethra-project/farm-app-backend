from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

fpo_profile_bp = Blueprint("fpo_profile_bp", __name__, url_prefix="/fpo")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@fpo_profile_bp.route("/profile", methods=["GET", "POST"])
def manage_fpo():
    user_id = session.get("user_id")
    if not user_id:
        return api_response("error", message="Unauthorized.", http_status=401)

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        db.session.execute(
            text("""
                INSERT INTO fpo_profiles (user_id, fpo_name, registration_number, district, state, pincode, contact_person, bank_account_no, ifsc_code)
                VALUES (:uid, :name, :reg, :district, :state, :pincode, :contact, :bank, :ifsc)
                ON DUPLICATE KEY UPDATE 
                    fpo_name=VALUES(fpo_name), district=VALUES(district), state=VALUES(state),
                    pincode=VALUES(pincode), contact_person=VALUES(contact_person)
            """),
            {
                "uid": user_id, "name": payload.get("fpo_name"), "reg": payload.get("registration_number"),
                "district": payload.get("district"), "state": payload.get("state"), "pincode": payload.get("pincode"),
                "contact": payload.get("contact_person"), "bank": payload.get("bank_account_no"), "ifsc": payload.get("ifsc_code")
            }
        )
        db.session.commit()
        return api_response("success", message="FPO profile saved.")

    fpo = db.session.execute(text("SELECT * FROM fpo_profiles WHERE user_id = :uid"), {"uid": user_id}).mappings().first()
    return api_response("success", data=dict(fpo) if fpo else {})
