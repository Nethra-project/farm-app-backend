from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

farmer_profile_bp = Blueprint("farmer_profile_bp", __name__, url_prefix="/farmer")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@farmer_profile_bp.route("/profile", methods=["GET", "POST"])
def manage_profile():
    user_id = session.get("user_id")
    if not user_id:
        return api_response("error", message="Unauthorized.", http_status=401)

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        db.session.execute(
            text("""
                INSERT INTO farmer_profiles (user_id, full_name, village, district, state, pincode, crops_grown, upi_id, bank_account_no, ifsc_code)
                VALUES (:uid, :name, :village, :district, :state, :pincode, :crops, :upi, :bank, :ifsc)
                ON DUPLICATE KEY UPDATE 
                    full_name=VALUES(full_name), village=VALUES(village), district=VALUES(district),
                    state=VALUES(state), pincode=VALUES(pincode), crops_grown=VALUES(crops_grown),
                    upi_id=VALUES(upi_id), bank_account_no=VALUES(bank_account_no), ifsc_code=VALUES(ifsc_code)
            """),
            {
                "uid": user_id, "name": payload.get("full_name"), "village": payload.get("village"),
                "district": payload.get("district"), "state": payload.get("state"), "pincode": payload.get("pincode"),
                "crops": payload.get("crops_grown"), "upi": payload.get("upi_id"), "bank": payload.get("bank_account_no"),
                "ifsc": payload.get("ifsc_code")
            }
        )
        db.session.commit()
        return api_response("success", message="Farmer profile updated.")

    profile = db.session.execute(
        text("SELECT * FROM farmer_profiles WHERE user_id = :uid"),
        {"uid": user_id}
    ).mappings().first()
    return api_response("success", data=dict(profile) if profile else {})
