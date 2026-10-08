from flask import Blueprint, jsonify, request
from sqlalchemy import text
from database import db

utils_bp = Blueprint("utils_bp", __name__, url_prefix="/utils")

@utils_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "success", "message": "API services active."})

@utils_bp.route("/mandi-prices", methods=["GET"])
def get_mandi_prices():
    crop = request.args.get("crop")
    district = request.args.get("district")

    query = "SELECT * FROM mandi_prices WHERE 1=1"
    params = {}
    if crop:
        query += " AND crop_name = :crop"
        params["crop"] = crop
    if district:
        query += " AND district = :district"
        params["district"] = district

    prices = db.session.execute(text(query), params).mappings().all()
    return jsonify({"status": "success", "data": [dict(p) for p in prices]})
