from app.extensions import db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.services.cart_service import get_or_create_cart
from app.services import event_service
from app.utils.helpers import ApiError


def checkout(user_id, session_id=None):
    cart = get_or_create_cart(user_id)

    if not cart.items:
        raise ApiError("Cart is empty", status_code=400)

    # Re-validate stock for every item before committing anything, so a
    # partially-processed order can never be created.
    for item in cart.items:
        if item.product is None:
            raise ApiError(f"Product for cart item {item.id} no longer exists", status_code=400)
        if item.product.stock < item.quantity:
            raise ApiError(f"Not enough stock for '{item.product.name}'", status_code=400)

    total_amount = sum(float(item.product.price) * item.quantity for item in cart.items)

    order = Order(user_id=user_id, total_amount=total_amount, status=OrderStatus.COMPLETED.value)
    db.session.add(order)
    db.session.flush()  # get order.id before creating order items

    order_items_data = []
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            unit_price=item.product.price,
            quantity=item.quantity,
        )
        db.session.add(order_item)
        order_items_data.append((item.product_id, item.quantity))

        # Decrement stock now that the purchase is confirmed.
        item.product.stock -= item.quantity

    # Clear the cart now that the order has been created.
    CartItem.query.filter_by(cart_id=cart.id).delete()

    db.session.commit()

    # Record a purchase event per product so the AI team's event stream
    # reflects exactly what was bought.
    for product_id, quantity in order_items_data:
        event_service.log_event(
            session_id=session_id or f"checkout-user-{user_id}",
            event_type="purchase",
            user_id=user_id,
            product_id=product_id,
            metadata={"order_id": order.id, "quantity": quantity},
        )

    return order
