from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

listings_bp = Blueprint("listings_bp", __name__, url_prefix="/listings")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@listings_bp.route("", methods=["GET", "POST"])
def handle_listings():
    user_id = session.get("user_id")

    if request.method == "POST":
        if not user_id: return api_response("error", message="Unauthorized.", http_status=401)
        payload = request.get_json(silent=True) or {}
        
        db.session.execute(
            text("""
                INSERT INTO listings (farmer_id, crop_name, category, quantity, unit, price_per_unit, district, description)
                VALUES (:fid, :crop, :cat, :qty, :unit, :price, :district, :desc)
            """),
            {
                "fid": user_id, "crop": payload.get("crop_name"), "cat": payload.get("category", "vegetables"),
                "qty": payload.get("quantity"), "unit": payload.get("unit", "kg"), "price": payload.get("price_per_unit"),
                "district": payload.get("district"), "desc": payload.get("description")
            }
        )
        db.session.commit()
        return api_response("success", message="Crop listing published.", http_status=201)

    listings = db.session.execute(text("SELECT * FROM listings WHERE status = 'active' ORDER BY created_at DESC")).mappings().all()
    return api_response("success", data=[dict(l) for l in listings])
