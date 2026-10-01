from flask import jsonify


def success_response(message="Success", data=None, status_code=200):
    """Build the standard success envelope used across every endpoint."""
    payload = {"success": True, "message": message, "data": data if data is not None else {}}
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Build the standard error envelope. Never leaks stack traces or
    internal exception details to the client."""
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code


class ApiError(Exception):
    """Raised by services/routes to signal an error that should be turned
    into a clean JSON error response with a specific HTTP status code."""

    def __init__(self, message, status_code=400, errors=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def to_decimal_str(value):
    """Safely format a Decimal/float price as a fixed 2-decimal string-friendly
    float, avoiding floating point surprises when returning JSON."""
    if value is None:
        return None
    return float(value)
