from app.extensions import db
from app.models.product import Product
from app.utils.helpers import ApiError


def list_products(page=1, per_page=20, category=None, search=None):
    query = Product.query

    if category:
        query = query.filter(Product.category.ilike(category))

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(Product.name.ilike(like_pattern))

    query = query.order_by(Product.id.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        raise ApiError("Product not found", status_code=404)
    return product


def create_product(data):
    product = Product(
        name=data["name"],
        description=data.get("description"),
        category=data.get("category"),
        price=data["price"],
        stock=data.get("stock", 0),
        image_url=data.get("image_url"),
    )
    db.session.add(product)
    db.session.commit()
    return product


def update_product(product_id, data):
    product = get_product(product_id)
    for field in ("name", "description", "category", "price", "stock", "image_url"):
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return product


def delete_product(product_id):
    product = get_product(product_id)
    db.session.delete(product)
    db.session.commit()
