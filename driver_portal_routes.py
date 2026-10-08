from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from database import db

driver_portal_bp = Blueprint("driver_portal_bp", __name__, url_prefix="/driver")

def api_response(status, data=None, message="", http_status=200):
    return jsonify({"status": status, "data": data, "message": message}), http_status

@driver_portal_bp.route("/jobs/available", methods=["GET"])
def available_jobs():
    driver_id = session.get("user_id")
    if not driver_id or session.get("approval_status") == "pending":
        return api_response("error", message="Account not authorized or pending approval.", http_status=403)

    jobs = db.session.execute(text("SELECT * FROM delivery_jobs WHERE status = 'open'")).mappings().all()
    return api_response("success", data=[dict(j) for j in jobs])

@driver_portal_bp.route("/jobs/<int:job_id>/accept", methods=["POST"])
def accept_job(job_id):
    driver_id = session.get("user_id")
    if not driver_id: return api_response("error", message="Unauthorized.", http_status=401)

    res = db.session.execute(
        text("UPDATE delivery_jobs SET status = 'accepted', driver_id = :did WHERE id = :jid AND status = 'open'"),
        {"did": driver_id, "jid": job_id}
    )
    db.session.commit()

    if res.rowcount == 0:
        return api_response("error", message="Job already taken.", http_status=409)

    return api_response("success", message="Job accepted.")
