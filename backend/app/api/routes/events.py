from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError

from app.schemas.event import event_create_schema
from app.services import event_service
from app.utils.helpers import success_response, error_response, ApiError

events_bp = Blueprint("events", __name__)


def _get_optional_user_id():
    """Events can be logged by anonymous visitors (e.g. a click before
    login), so authentication is optional here. If a valid JWT is present
    we attach the user_id; otherwise the event is stored with user_id=None."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity is not None else None
    except Exception:
        return None


@events_bp.route("", methods=["POST"])
def create_event():
    try:
        data = event_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Invalid event data", status_code=400, errors=err.messages)

    user_id = _get_optional_user_id()

    try:
        event = event_service.log_event(
            session_id=data["session_id"],
            event_type=data["event_type"],
            user_id=user_id,
            product_id=data.get("product_id"),
            metadata=data.get("metadata"),
        )
    except ApiError as err:
        return error_response(err.message, status_code=err.status_code)

    return success_response("Event logged", data={"event": event.to_dict()}, status_code=201)


@events_bp.route("", methods=["GET"])
@jwt_required()
def list_events():
    """Simple read-only endpoint so the AI team (or an internal dashboard)
    can sanity-check recent events without connecting to Postgres directly.
    The heavy analytical querying still happens via Pandas/DuckDB on the DB."""
    session_id = request.args.get("session_id")
    event_type = request.args.get("event_type")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=50, type=int)

    pagination = event_service.list_events(
        session_id=session_id, event_type=event_type, page=page, per_page=per_page
    )

    return success_response(
        "Events retrieved",
        data={
            "events": [e.to_dict() for e in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        },
    )
