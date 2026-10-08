from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

orders_bp = Blueprint("orders_bp", __name__, url_prefix="/orders")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@orders_bp.route("", methods=["GET"])
def get_orders():
    user_id = session.get("user_id")
    if not user_id: return api_response("error", message="Unauthorized.", http_status=401)

    orders = db.session.execute(
        text("SELECT * FROM orders WHERE farmer_id = :uid OR buyer_id = :uid ORDER BY created_at DESC"),
        {"uid": user_id}
    ).mappings().all()
    
    return api_response("success", data=[dict(o) for o in orders])
