from app.extensions import db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.utils.helpers import ApiError


def get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:
        return cart

    cart = Cart(user_id=user_id)
    db.session.add(cart)
    db.session.commit()
    return cart


def get_cart(user_id):
    return get_or_create_cart(user_id)


def add_item(user_id, product_id, quantity):
    product = Product.query.get(product_id)
    if not product:
        raise ApiError("Product not found", status_code=404)

    if quantity < 1:
        raise ApiError("Quantity must be at least 1", status_code=400)

    if product.stock < quantity:
        raise ApiError("Not enough stock available", status_code=400)

    cart = get_or_create_cart(user_id)

    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        new_quantity = item.quantity + quantity
        if product.stock < new_quantity:
            raise ApiError("Not enough stock available", status_code=400)
        item.quantity = new_quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return cart


def update_item_quantity(user_id, item_id, quantity):
    cart = get_or_create_cart(user_id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise ApiError("Cart item not found", status_code=404)

    if quantity < 1:
        raise ApiError("Quantity must be at least 1", status_code=400)

    if item.product.stock < quantity:
        raise ApiError("Not enough stock available", status_code=400)

    item.quantity = quantity
    db.session.commit()
    return cart


def remove_item(user_id, item_id):
    cart = get_or_create_cart(user_id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise ApiError("Cart item not found", status_code=404)

    db.session.delete(item)
    db.session.commit()
    return cart


def clear_cart(user_id):
    cart = get_or_create_cart(user_id)
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()
    return cart
