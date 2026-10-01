from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.cart import add_cart_item_schema, update_cart_item_schema
from app.services import cart_service, event_service
from app.utils.helpers import success_response, error_response, ApiError

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    cart = cart_service.get_cart(user_id)
    return success_response("Cart retrieved", data={"cart": cart.to_dict()})


@cart_bp.route("", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    body = request.get_json(silent=True) or {}

    try:
        data = add_cart_item_schema.load(body)
    except ValidationError as err:
        return error_response("Invalid cart item data", status_code=400, errors=err.messages)

    try:
        cart = cart_service.add_item(user_id, data["product_id"], data["quantity"])
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    # Log the add_to_cart interaction for the AI team's event stream.
    # session_id is optional here; fall back to a per-user pseudo session
    # so the event is never dropped just because the frontend omitted it.
    session_id = body.get("session_id") or f"user-{user_id}"
    try:
        event_service.log_event(
            session_id=session_id,
            event_type="add_to_cart",
            user_id=user_id,
            product_id=data["product_id"],
            metadata={"quantity": data["quantity"], "source": body.get("source", "cart_api")},
        )
    except ApiError:
        # Event logging must never block the cart operation itself.
        pass

    return success_response("Product added to cart", data={"cart": cart.to_dict()}, status_code=201)


@cart_bp.route("/<int:item_id>", methods=["PATCH"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())

    try:
        data = update_cart_item_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid cart item data", status_code=400, errors=err.messages)

    try:
        cart = cart_service.update_item_quantity(user_id, item_id, data["quantity"])
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Cart item updated", data={"cart": cart.to_dict()})


@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_cart_item(item_id):
    user_id = int(get_jwt_identity())

    try:
        cart = cart_service.remove_item(user_id, item_id)
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Product removed from cart", data={"cart": cart.to_dict()})


@cart_bp.route("", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    cart = cart_service.clear_cart(user_id)
    return success_response("Cart cleared", data={"cart": cart.to_dict()})
