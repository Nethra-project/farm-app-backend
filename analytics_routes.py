from flask import Blueprint, jsonify, session
from sqlalchemy import text
from database import db

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/analytics")

@analytics_bp.route("/farmer-summary", methods=["GET"])
def farmer_summary():
    user_id = session.get("user_id")
    if not user_id: return jsonify({"status": "error", "message": "Unauthorized"}), 401

    stats = db.session.execute(
        text("""
            SELECT 
                COUNT(id) as total_orders,
                COALESCE(SUM(farmer_price_total), 0.0) as total_earnings
            FROM orders WHERE farmer_id = :uid AND status = 'delivered'
        """),
        {"uid": user_id}
    ).mappings().first()

    return jsonify({"status": "success", "data": dict(stats)})
