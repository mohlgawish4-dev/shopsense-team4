from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.checkout import checkout_schema
from app.services import checkout_service
from app.models.order import Order
from app.utils.helpers import success_response, error_response, ApiError

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/checkout", methods=["POST"])
@jwt_required()
def do_checkout():
    user_id = int(get_jwt_identity())

    try:
        data = checkout_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid checkout data", status_code=400, errors=err.messages)

    try:
        order = checkout_service.checkout(user_id, session_id=data.get("session_id"))
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Order placed successfully", data={"order": order.to_dict()}, status_code=201)


@checkout_bp.route("/orders", methods=["GET"])
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    pagination = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return success_response(
        "Orders retrieved",
        data={
            "orders": [o.to_dict() for o in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        },
    )


@checkout_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return error_response("Order not found", status_code=404)

    return success_response("Order retrieved", data={"order": order.to_dict()})
