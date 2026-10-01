from datetime import datetime, timezone

from app.extensions import db

try:
    from sqlalchemy.dialects.postgresql import JSONB as JSONType
except ImportError:  # pragma: no cover - fallback for non-postgres testing
    from sqlalchemy import JSON as JSONType


class EventType(str):
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    VIEW_PRODUCT = "view_product"
    SEARCH = "search"


VALID_EVENT_TYPES = {
    EventType.CLICK,
    EventType.ADD_TO_CART,
    EventType.PURCHASE,
    EventType.VIEW_PRODUCT,
    EventType.SEARCH,
}


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = db.Column(db.String(120), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    event_metadata = db.Column(JSONType, nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user = db.relationship("User", back_populates="events")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "product_id": self.product_id,
            "metadata": self.event_metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
