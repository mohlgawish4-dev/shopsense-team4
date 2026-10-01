from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.auth import register_schema, login_schema
from app.services import auth_service
from app.utils.helpers import success_response, error_response, ApiError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid registration data", status_code=400, errors=err.messages)

    try:
        user, token = auth_service.register_user(
            email=data["email"], password=data["password"], full_name=data.get("full_name")
        )
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code, errors=err.errors)

    return success_response(
        "User registered successfully",
        data={"user": user.to_dict(), "access_token": token},
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid login data", status_code=400, errors=err.messages)

    try:
        user, token = auth_service.login_user(email=data["email"], password=data["password"])
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code, errors=err.errors)

    return success_response(
        "Login successful", data={"user": user.to_dict(), "access_token": token}
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    try:
        user = auth_service.get_user_by_id(get_jwt_identity())
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Current user", data={"user": user.to_dict()})
