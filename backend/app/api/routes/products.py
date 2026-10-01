from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.schemas.product import product_create_schema, product_update_schema
from app.services import product_service
from app.utils.helpers import success_response, error_response, ApiError

products_bp = Blueprint("products", __name__)


@products_bp.route("", methods=["GET"])
def list_products():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    category = request.args.get("category")
    search = request.args.get("search")

    pagination = product_service.list_products(page=page, per_page=per_page, category=category, search=search)

    return success_response(
        "Products retrieved",
        data={
            "products": [p.to_dict() for p in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        },
    )


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = product_service.get_product(product_id)
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Product retrieved", data={"product": product.to_dict()})


@products_bp.route("", methods=["POST"])
@jwt_required()
def create_product():
    try:
        data = product_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid product data", status_code=400, errors=err.messages)

    product = product_service.create_product(data)
    return success_response("Product created", data={"product": product.to_dict()}, status_code=201)


@products_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    try:
        data = product_update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid product data", status_code=400, errors=err.messages)

    try:
        product = product_service.update_product(product_id, data)
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Product updated", data={"product": product.to_dict()})


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    try:
        product_service.delete_product(product_id)
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Product deleted")
