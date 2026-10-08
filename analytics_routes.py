from datetime import datetime
from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/analytics")

# Status constants
LISTING_ACTIVE = "active"
ORDER_NEW = "new"
ORDER_IN_PROGRESS = ("accepted", "in_progress", "out_for_delivery")
ORDER_DELIVERED = "delivered"
PAYMENT_PAID = "paid"
PAYMENT_METHODS = ("COD", "UPI")

# Helpers
def api_response(status, data=None, message="", http_code=200):
    return jsonify({"status": status, "data": data, "message": message}), http_code

def success(data=None, message="Ok", http_code=200):
    return api_response("success", data, message, http_code)

def error(message, http_code=400, data=None):
    return api_response("error", data, message, http_code)

def to_float(value, places=2):
    if value is None:
        return None
    if isinstance(value, Decimal):
        value = float(value)
    return round(float(value), places)

def get_farmer_id():
    raw = session.get("user_id") or request.headers.get("X-Farmer-Id") or request.args.get("farmer_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

# 1. Dashboard summary
@analytics_bp.route("/dashboard-summary", methods=["GET"])
def get_dashboard_summary():
    farmer_id = get_farmer_id()
    if farmer_id is None:
        return error("Farmer identification is required.", 401)
    try:
        listing_row = db.session.execute(
            text("""
                SELECT COUNT(*) AS active_listings
                FROM listings
                WHERE farmer_id = :farmer_id AND status = :active
            """),
            {"farmer_id": farmer_id, "active": LISTING_ACTIVE},
        ).mappings().first()

        order_row = db.session.execute(
            text("""
                SELECT
                    COALESCE(SUM(CASE WHEN status = :new_status THEN 1 ELSE 0 END), 0) AS new_orders,
                    COALESCE(SUM(CASE WHEN status IN :in_progress THEN 1 ELSE 0 END), 0) AS in_progress_orders,
                    COALESCE(SUM(CASE WHEN status = :delivered THEN farmer_price_total ELSE 0 END), 0) AS total_earnings
                FROM orders
                WHERE farmer_id = :farmer_id
            """).bindparams(db.bindparam("in_progress", expanding=True)),
            {
                "farmer_id": farmer_id,
                "new_status": ORDER_NEW,
                "in_progress": list(ORDER_IN_PROGRESS),
                "delivered": ORDER_DELIVERED,
            },
        ).mappings().first()

        data = {
            "active_listings": int(listing_row["active_listings"] or 0),
            "new_orders": int(order_row["new_orders"] or 0),
            "in_progress_orders": int(order_row["in_progress_orders"] or 0),
            "total_earnings": to_float(order_row["total_earnings"]) or 0.0,
        }
        return success(data, "Dashboard summary fetched successfully.")
    except SQLAlchemyError as exc:
        db.session.rollback()
        return error(f"Database error: {str(exc._cause or exc)}", 500)
    except Exception as exc:
        return error(f"Unexpected error: {exc}", 500)

# 2. Mandi price hint
@analytics_bp.route("/mandi-price", methods=["GET"])
def get_mandi_price_hint():
    crop_name = (request.args.get("crop_name") or "").strip()
    district = (request.args.get("district") or "").strip()
    if not crop_name or not district:
        return error("Both 'crop_name' and 'district' query parameters are required.", 400)
    try:
        row = db.session.execute(
            text("""
                SELECT crop_name, district, mandi_price_per_unit, unit, updated_at
                FROM mandi_prices
                WHERE LOWER(crop_name) = LOWER(:crop_name)
                  AND LOWER(district) = LOWER(:district)
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
            """),
            {"crop_name": crop_name, "district": district},
        ).mappings().first()

        if row:
            data = {
                "crop_name": row["crop_name"],
                "district": row["district"],
                "mandi_price_per_unit": to_float(row["mandi_price_per_unit"]),
                "unit": row["unit"] or "kg",
                "updated_at": row["updated_at"].isoformat(),
                "is_district_specific": True,
            }
            return success(data, "Mandi benchmark price fetched successfully.")

        fallback = db.session.execute(
            text("""
                SELECT
                    MIN(mp.crop_name) AS crop_name,
                    AVG(mp.mandi_price_per_unit) AS avg_price,
                    MIN(mp.unit) AS unit,
                    MAX(mp.updated_at) AS updated_at
                FROM mandi_prices mp
                JOIN (
                    SELECT district, MAX(updated_at) AS max_date
                    FROM mandi_prices
                    WHERE LOWER(crop_name) = LOWER(:crop_name)
                    GROUP BY district
                ) latest
                ON latest.district = mp.district AND latest.max_date = mp.updated_at
                WHERE LOWER(mp.crop_name) = LOWER(:crop_name)
            """),
            {"crop_name": crop_name},
        ).mappings().first()

        if fallback and fallback["avg_price"] is not None:
            data = {
                "crop_name": fallback["crop_name"],
                "district": district,
                "mandi_price_per_unit": to_float(fallback["avg_price"]),
                "unit": fallback["unit"] or "kg",
                "updated_at": fallback["updated_at"].isoformat(),
                "is_district_specific": False,
            }
            return success(
                data,
                f"No rate found for '{district}'. Showing average across other districts.",
            )
        return error(f"No mandi price found for crop '{crop_name}'.", 404)
    except SQLAlchemyError as exc:
        db.session.rollback()
        return error(f"Database error: {str(exc._cause or exc)}", 500)
    except Exception as exc:
        return error(f"Unexpected error: {exc}", 500)

# 3. Farmer earnings report
@analytics_bp.route("/earnings-report", methods=["GET"])
def get_farmer_earnings_report():
    farmer_id = get_farmer_id()
    if farmer_id is None:
        return error("Farmer identification is required.", 401)

    try:
        from_date = parse_date(request.args["from_date"]) if request.args.get("from_date") else None
        to_date = parse_date(request.args["to_date"]) if request.args.get("to_date") else None
    except ValueError:
        return error("Dates must be in YYYY-MM-DD format.", 400)

    if from_date and to_date and from_date > to_date:
        return error("'from_date' cannot be after 'to_date'.", 400)

    params = {"farmer_id": farmer_id, "delivered": ORDER_DELIVERED, "paid": PAYMENT_PAID}
    date_sql = ""
    if from_date:
        date_sql += " AND DATE(o.created_at) >= :from_date"
        params["from_date"] = from_date
    if to_date:
        date_sql += " AND DATE(o.created_at) <= :to_date"
        params["to_date"] = to_date

    try:
        payout_rows = db.session.execute(
            text(f"""
                SELECT
                    UPPER(o.payment_method) AS payment_method,
                    COUNT(*) AS order_count,
                    COALESCE(SUM(o.farmer_price_total), 0) AS total,
                    COALESCE(SUM(CASE WHEN o.payment_status = :paid THEN o.farmer_price_total ELSE 0 END), 0) AS completed,
                    COALESCE(SUM(CASE WHEN o.payment_status <> :paid THEN o.farmer_price_total ELSE 0 END), 0) AS pending
                FROM orders o
                WHERE o.farmer_id = :farmer_id
                  AND o.status = :delivered
                  {date_sql}
                GROUP BY UPPER(o.payment_method)
            """),
            params,
        ).mappings().all()

        by_method = {
            m: {"order_count": 0, "total": 0.0, "completed_payout": 0.0, "pending_payout": 0.0}
            for m in PAYMENT_METHODS
        }
        total_earned = completed_total = pending_total = 0.0

        for r in payout_rows:
            method = r["payment_method"]
            bucket = by_method.setdefault(
                method,
                {"order_count": 0, "total": 0.0, "completed_payout": 0.0, "pending_payout": 0.0},
            )
            bucket["order_count"] = int(r["order_count"])
            bucket["total"] = to_float(r["total"])
            bucket["completed_payout"] = to_float(r["completed"])
            bucket["pending_payout"] = to_float(r["pending"])
            total_earned += float(r["total"])
            completed_total += float(r["completed"])
            pending_total += float(r["pending"])

        realization_rows = db.session.execute(
            text(f"""
                SELECT
                    o.id AS order_id,
                    l.crop_name,
                    l.district,
                    COALESCE(l.unit, 'kg') AS unit,
                    o.quantity,
                    o.farmer_price_total,
                    DATE(o.created_at) AS order_date,
                    COALESCE(
                        (SELECT mp.mandi_price_per_unit
                         FROM mandi_prices mp
                         WHERE LOWER(mp.crop_name) = LOWER(l.crop_name)
                           AND LOWER(mp.district) = LOWER(l.district)
                           AND mp.updated_at <= DATE(o.created_at)
                         ORDER BY mp.updated_at DESC, mp.id DESC
                         LIMIT 1),
                        (SELECT mp2.mandi_price_per_unit
                         FROM mandi_prices mp2
                         WHERE LOWER(mp2.crop_name) = LOWER(l.crop_name)
                           AND LOWER(mp2.district) = LOWER(l.district)
                         ORDER BY mp2.updated_at DESC, mp2.id DESC
                         LIMIT 1)
                    ) AS mandi_rate
                FROM orders o
                JOIN listings l ON l.id = o.listing_id
                WHERE o.farmer_id = :farmer_id
                  AND o.status = :delivered
                  {date_sql}
                ORDER BY o.created_at DESC
            """),
            params,
        ).mappings().all()

        comparisons = []
        sum_farmer_value = 0.0
        sum_mandi_value = 0.0

        for r in realization_rows:
            qty = float(r["quantity"] or 0)
            farmer_total = float(r["farmer_price_total"] or 0)
            farmer_per_unit = round(farmer_total / qty, 2) if qty > 0 else None
            mandi_rate = to_float(r["mandi_rate"])
            mandi_total = None
            difference_per_unit = None
            realization_pct = None

            if mandi_rate is not None and qty > 0:
                mandi_total = round(mandi_rate * qty, 2)
                difference_per_unit = round(farmer_per_unit - mandi_rate, 2)
                realization_pct = round((farmer_total / mandi_total) * 100, 2) if mandi_total > 0 else None
                sum_farmer_value += farmer_total
                sum_mandi_value += mandi_total

            comparisons.append({
                "order_id": r["order_id"],
                "crop_name": r["crop_name"],
                "district": r["district"],
                "order_date": r["order_date"].isoformat() if r["order_date"] else None,
                "quantity": to_float(qty),
                "unit": r["unit"],
                "farmer_price_total": round(farmer_total, 2),
                "farmer_price_per_unit": farmer_per_unit,
                "mandi_rate_per_unit": mandi_rate,
                "mandi_value_total": mandi_total,
                "difference_per_unit": difference_per_unit,
                "realization_percent": realization_pct,
            })

        overall_realization = (
            round((sum_farmer_value / sum_mandi_value) * 100, 2)
            if sum_mandi_value > 0
            else None
        )

        data = {
            "farmer_id": farmer_id,
            "period": {
                "from_date": from_date.isoformat() if from_date else None,
                "to_date": to_date.isoformat() if to_date else None,
            },
            "total_earned": round(total_earned, 2),
            "payouts": {
                "completed": round(completed_total, 2),
                "pending": round(pending_total, 2),
                "by_payment_method": by_method,
            },
            "price_realization": {
                "overall_realization_percent": overall_realization,
                "farmer_value_compared": round(sum_farmer_value, 2),
                "mandi_value_compared": round(sum_mandi_value, 2),
                "orders_without_mandi_rate": sum(
                    1 for c in comparisons if c["mandi_rate_per_unit"] is None
                ),
                "orders": comparisons,
            },
        }
        return success(data, "Earnings report generated successfully.")
    except SQLAlchemyError as exc:
        db.session.rollback()
        return error(f"Database error: {str(exc._cause or exc)}", 500)
    except Exception as exc:
        return error(f"Unexpected error: {exc}", 500)
