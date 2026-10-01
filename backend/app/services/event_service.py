from app.extensions import db
from app.models.event import Event, VALID_EVENT_TYPES
from app.models.product import Product
from app.utils.helpers import ApiError

# Event types that must reference a real product, since they are
# meaningless to the AI layer without one.
PRODUCT_REQUIRED_EVENTS = {"add_to_cart", "purchase", "view_product"}


def log_event(session_id, event_type, user_id=None, product_id=None, metadata=None):
    """Reusable event logger. Called directly from the /api/events route and
    internally by other services (e.g. checkout logs a 'purchase' event)."""

    if event_type not in VALID_EVENT_TYPES:
        raise ApiError(f"Invalid event_type '{event_type}'", status_code=400)

    if not session_id:
        raise ApiError("session_id is required", status_code=400)

    if event_type in PRODUCT_REQUIRED_EVENTS and not product_id:
        raise ApiError(f"product_id is required for event_type '{event_type}'", status_code=400)

    if product_id is not None:
        product = Product.query.get(product_id)
        if not product:
            raise ApiError("Product not found", status_code=404)

    if metadata is not None and not isinstance(metadata, dict):
        raise ApiError("metadata must be a JSON object", status_code=400)

    event = Event(
        user_id=user_id,
        session_id=session_id,
        event_type=event_type,
        product_id=product_id,
        event_metadata=metadata,
    )
    db.session.add(event)
    db.session.commit()
    return event


def list_events(user_id=None, session_id=None, event_type=None, page=1, per_page=50):
    query = Event.query

    if user_id is not None:
        query = query.filter(Event.user_id == user_id)
    if session_id is not None:
        query = query.filter(Event.session_id == session_id)
    if event_type is not None:
        query = query.filter(Event.event_type == event_type)

    query = query.order_by(Event.timestamp.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)
