from flask import Blueprint, request, jsonify, session
from database import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


farmer_profile_bp = Blueprint(
    "farmer_profile_bp",
    __name__,
    url_prefix="/farmer"
)


def api_response(status, data=None, message="", http_status=200):
    """
    Standard API response format.
    """
    return jsonify({
        "status": status,
        "data": data,
        "message": message
    }), http_status


def get_logged_in_user_id():
    """
    Returns the authenticated user's ID from the Flask session.
    """
    return session.get("user_id")


@farmer_profile_bp.route("/profile", methods=["POST"])
def save_farmer_profile():
    """
    Create or replace/update the farmer profile belonging to the
    currently logged-in user.
    """

    user_id = get_logged_in_user_id()

    if not user_id:
        return api_response(
            status="error",
            data=None,
            message="Authentication required.",
            http_status=401
        )

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return api_response(
            status="error",
            data=None,
            message="A valid JSON request body is required.",
            http_status=400
        )

    required_fields = [
        "full_name",
        "village",
        "district",
        "state",
        "pincode"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing_fields:
        return api_response(
            status="error",
            data={"missing_fields": missing_fields},
            message="Required profile information is missing.",
            http_status=400
        )

    profile_data = {
        "user_id": user_id,
        "full_name": str(payload["full_name"]).strip(),
        "village": str(payload["village"]).strip(),
        "district": str(payload["district"]).strip(),
        "state": str(payload["state"]).strip(),
        "pincode": str(payload["pincode"]).strip(),
        "crops_grown": (
            str(payload["crops_grown"]).strip()
            if payload.get("crops_grown") is not None
            else None
        ),
        "upi_id": (
            str(payload["upi_id"]).strip()
            if payload.get("upi_id") is not None
            else None
        ),
        "bank_account_no": (
            str(payload["bank_account_no"]).strip()
            if payload.get("bank_account_no") is not None
            else None
        ),
        "ifsc_code": (
            str(payload["ifsc_code"]).strip().upper()
            if payload.get("ifsc_code") is not None
            else None
        ),
        "fpo_id": payload.get("fpo_id"),
        "profile_photo_url": (
            str(payload["profile_photo_url"]).strip()
            if payload.get("profile_photo_url") is not None
            else None
        )
    }

    try:
        existing_profile = db.session.execute(
            text("""
                SELECT id
                FROM farmer_profiles
                WHERE user_id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        if existing_profile:
            db.session.execute(
                text("""
                    UPDATE farmer_profiles
                    SET
                        full_name = :full_name,
                        village = :village,
                        district = :district,
                        state = :state,
                        pincode = :pincode,
                        crops_grown = :crops_grown,
                        upi_id = :upi_id,
                        bank_account_no = :bank_account_no,
                        ifsc_code = :ifsc_code,
                        fpo_id = :fpo_id,
                        profile_photo_url = :profile_photo_url
                    WHERE user_id = :user_id
                """),
                profile_data
            )

            message = "Farmer profile updated successfully."

        else:
            db.session.execute(
                text("""
                    INSERT INTO farmer_profiles (
                        user_id,
                        full_name,
                        village,
                        district,
                        state,
                        pincode,
                        crops_grown,
                        upi_id,
                        bank_account_no,
                        ifsc_code,
                        fpo_id,
                        profile_photo_url
                    )
                    VALUES (
                        :user_id,
                        :full_name,
                        :village,
                        :district,
                        :state,
                        :pincode,
                        :crops_grown,
                        :upi_id,
                        :bank_account_no,
                        :ifsc_code,
                        :fpo_id,
                        :profile_photo_url
                    )
                """),
                profile_data
            )

            message = "Farmer profile created successfully."

        db.session.commit()

        profile = db.session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    full_name,
                    village,
                    district,
                    state,
                    pincode,
                    crops_grown,
                    upi_id,
                    bank_account_no,
                    ifsc_code,
                    fpo_id,
                    profile_photo_url
                FROM farmer_profiles
                WHERE user_id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        return api_response(
            status="success",
            data=dict(profile) if profile else None,
            message=message,
            http_status=200 if existing_profile else 201
        )

    except SQLAlchemyError:
        db.session.rollback()

        return api_response(
            status="error",
            data=None,
            message="Unable to save farmer profile.",
            http_status=500
        )


@farmer_profile_bp.route("/profile", methods=["GET"])
def get_farmer_profile():
    """
    Return the currently logged-in farmer's user and profile information.
    """

    user_id = get_logged_in_user_id()

    if not user_id:
        return api_response(
            status="error",
            data=None,
            message="Authentication required.",
            http_status=401
        )

    try:
        result = db.session.execute(
            text("""
                SELECT
                    u.*,
                    fp.id AS farmer_profile_id,
                    fp.full_name,
                    fp.village,
                    fp.district,
                    fp.state,
                    fp.pincode,
                    fp.crops_grown,
                    fp.upi_id,
                    fp.bank_account_no,
                    fp.ifsc_code,
                    fp.fpo_id,
                    fp.profile_photo_url
                FROM users AS u
                INNER JOIN farmer_profiles AS fp
                    ON fp.user_id = u.id
                WHERE u.id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        if not result:
            return api_response(
                status="error",
                data=None,
                message="Farmer profile not found.",
                http_status=404
            )

        return api_response(
            status="success",
            data=dict(result),
            message="Farmer profile retrieved successfully.",
            http_status=200
        )

    except SQLAlchemyError:
        return api_response(
            status="error",
            data=None,
            message="Unable to retrieve farmer profile.",
            http_status=500
        )


@farmer_profile_bp.route("/profile", methods=["PUT"])
def update_farmer_profile():
    """
    Update editable farmer information.

    Editable categories:
    - Contact information stored on users
    - Village/location information
    - Bank/payment information
    - Crop information
    """

    user_id = get_logged_in_user_id()

    if not user_id:
        return api_response(
            status="error",
            data=None,
            message="Authentication required.",
            http_status=401
        )

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict) or not payload:
        return api_response(
            status="error",
            data=None,
            message="A valid JSON request body is required.",
            http_status=400
        )

    try:
        existing_profile = db.session.execute(
            text("""
                SELECT id
                FROM farmer_profiles
                WHERE user_id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        if not existing_profile:
            return api_response(
                status="error",
                data=None,
                message="Farmer profile not found.",
                http_status=404
            )

        # Profile fields the farmer is allowed to modify.
        allowed_profile_fields = {
            "village",
            "district",
            "state",
            "pincode",
            "crops_grown",
            "upi_id",
            "bank_account_no",
            "ifsc_code"
        }

        profile_updates = {}

        for field in allowed_profile_fields:
            if field in payload:
                value = payload[field]

                if isinstance(value, str):
                    value = value.strip()

                if field == "ifsc_code" and isinstance(value, str):
                    value = value.upper()

                profile_updates[field] = value

        # These fields cannot be empty because the SQL schema requires them.
        required_location_fields = {
            "village",
            "district",
            "state",
            "pincode"
        }

        for field in required_location_fields:
            if field in profile_updates and not profile_updates[field]:
                return api_response(
                    status="error",
                    data={"field": field},
                    message=f"{field} cannot be empty.",
                    http_status=400
                )

        if profile_updates:
            assignments = []

            parameters = {
                "user_id": user_id
            }

            for field, value in profile_updates.items():
                assignments.append(f"{field} = :{field}")
                parameters[field] = value

            query = text(
                """
                UPDATE farmer_profiles
                SET {}
                WHERE user_id = :user_id
                """.format(", ".join(assignments))
            )

            db.session.execute(query, parameters)

        # Contact fields are assumed to belong to users.
        # Only fields explicitly supplied by the client are changed.
        allowed_contact_fields = {
            "email",
            "phone"
        }

        contact_updates = {}

        for field in allowed_contact_fields:
            if field in payload:
                value = payload[field]

                if isinstance(value, str):
                    value = value.strip()

                if not value:
                    return api_response(
                        status="error",
                        data={"field": field},
                        message=f"{field} cannot be empty.",
                        http_status=400
                    )

                contact_updates[field] = value

        if contact_updates:
            assignments = []
            parameters = {
                "user_id": user_id
            }

            for field, value in contact_updates.items():
                assignments.append(f"{field} = :{field}")
                parameters[field] = value

            user_query = text(
                """
                UPDATE users
                SET {}
                WHERE id = :user_id
                """.format(", ".join(assignments))
            )

            db.session.execute(user_query, parameters)

        if not profile_updates and not contact_updates:
            return api_response(
                status="error",
                data=None,
                message="No editable profile fields were provided.",
                http_status=400
            )

        db.session.commit()

        updated_profile = db.session.execute(
            text("""
                SELECT
                    u.*,
                    fp.id AS farmer_profile_id,
                    fp.full_name,
                    fp.village,
                    fp.district,
                    fp.state,
                    fp.pincode,
                    fp.crops_grown,
                    fp.upi_id,
                    fp.bank_account_no,
                    fp.ifsc_code,
                    fp.fpo_id,
                    fp.profile_photo_url
                FROM users AS u
                INNER JOIN farmer_profiles AS fp
                    ON fp.user_id = u.id
                WHERE u.id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        return api_response(
            status="success",
            data=dict(updated_profile) if updated_profile else None,
            message="Farmer profile updated successfully.",
            http_status=200
        )

    except SQLAlchemyError:
        db.session.rollback()

        return api_response(
            status="error",
            data=None,
            message="Unable to update farmer profile.",
            http_status=500
        )


@farmer_profile_bp.route("/can-list", methods=["GET"])
def check_listing_eligibility():
    """
    Lock Engine.

    Farmers whose approval status is pending cannot create crop listings.
    """

    user_id = get_logged_in_user_id()

    if not user_id:
        return api_response(
            status="error",
            data=None,
            message="Authentication required.",
            http_status=401
        )

    approval_status = session.get("approval_status")

    if approval_status == "pending":
        return api_response(
            status="error",
            data={
                "can_list": False,
                "approval_status": "pending"
            },
            message="Account pending admin approval. You cannot list crops yet.",
            http_status=403
        )

    return api_response(
        status="success",
        data={
            "can_list": True,
            "approval_status": approval_status
        },
        message="Farmer is eligible to list crops.",
        http_status=200
    )
