from app.api.routes.auth import auth_bp
from app.api.routes.products import products_bp
from app.api.routes.cart import cart_bp
from app.api.routes.checkout import checkout_bp
from app.api.routes.events import events_bp


def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(checkout_bp, url_prefix="/api")
    app.register_blueprint(events_bp, url_prefix="/api/events")
