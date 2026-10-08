from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
import random
from database import db

buyer_portal_bp = Blueprint("buyer_portal_bp", __name__, url_prefix="/buyer")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@buyer_portal_bp.route("/orders/create", methods=["POST"])
def create_order():
    buyer_id = session.get("user_id")
    if not buyer_id: return api_response("error", message="Unauthorized.", http_status=401)

    payload = request.get_json(silent=True) or {}
    listing_id = payload.get("listing_id")
    quantity = float(payload.get("quantity", 0))

    listing = db.session.execute(text("SELECT * FROM listings WHERE id = :id AND status = 'active'"), {"id": listing_id}).mappings().first()
    if not listing: return api_response("error", message="Listing unavailable.", http_status=404)

    item_total = quantity * float(listing["price_per_unit"])
    delivery_code = str(random.randint(100000, 999999))

    order_res = db.session.execute(
        text("""
            INSERT INTO orders (listing_id, farmer_id, buyer_id, quantity, farmer_price_total, payment_method, delivery_code)
            VALUES (:lid, :fid, :bid, :qty, :total, :pay_method, :code)
        """),
        {
            "lid": listing_id, "fid": listing["farmer_id"], "bid": buyer_id,
            "qty": quantity, "total": item_total, "pay_method": payload.get("payment_method", "COD"),
            "code": delivery_code
        }
    )
    order_id = order_res.lastrowid

    # Create Delivery Job
    farmer_profile = db.session.execute(text("SELECT village, district FROM farmer_profiles WHERE user_id = :uid"), {"uid": listing["farmer_id"]}).mappings().first()
    db.session.execute(
        text("""
            INSERT INTO delivery_jobs (order_id, pickup_village, pickup_district, drop_city, drop_pincode, total_weight_kg, driver_pay, farmer_pickup_code, buyer_delivery_code)
            VALUES (:oid, :p_v, :p_d, :d_c, :d_p, :weight, :pay, :p_code, :d_code)
        """),
        {
            "oid": order_id, "p_v": farmer_profile["village"] if farmer_profile else "Farm",
            "p_d": listing["district"], "d_c": "Buyer City", "d_p": "000000",
            "weight": quantity, "pay": 150.00, "p_code": str(random.randint(100000, 999999)), "d_code": delivery_code
        }
    )
    db.session.commit()

    return api_response("success", data={"order_id": order_id}, message="Order placed successfully.", http_status=201)
