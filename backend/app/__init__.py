from flask import Flask
from marshmallow import ValidationError

from app.config import get_config
from app.extensions import db, migrate, jwt, cors
from app.utils.helpers import error_response, ApiError


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Models must be imported (even if unused directly) so Flask-Migrate
    # can discover every table when generating migrations.
    from app import models  # noqa: F401

    # Routes
    from app.api.routes import register_routes

    register_routes(app)

    register_error_handlers(app)

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"success": True, "message": "ShopSense backend is running"}, 200

    return app


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return error_response(err.message, status_code=err.status_code, errors=err.errors)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error_response("Invalid request data", status_code=400, errors=err.messages)

    @app.errorhandler(404)
    def handle_not_found(err):
        return error_response("Resource not found", status_code=404)

    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        return error_response("Method not allowed", status_code=405)

    @app.errorhandler(500)
    def handle_internal_error(err):
        # Never leak stack traces or internal details to the client.
        app.logger.exception("Unhandled exception")
        return error_response("An unexpected error occurred", status_code=500)
