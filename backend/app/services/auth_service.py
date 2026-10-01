from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user import User
from app.utils.helpers import ApiError


def register_user(email, password, full_name=None):
    existing = User.query.filter_by(email=email.lower().strip()).first()
    if existing:
        raise ApiError("An account with this email already exists", status_code=409)

    user = User(email=email.lower().strip(), full_name=full_name)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Every user gets an empty cart created up front so cart lookups never
    # have to special-case "user has no cart yet".
    from app.services.cart_service import get_or_create_cart

    get_or_create_cart(user.id)

    token = create_access_token(identity=str(user.id))
    return user, token


def login_user(email, password):
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not user.check_password(password):
        raise ApiError("Invalid email or password", status_code=401)

    token = create_access_token(identity=str(user.id))
    return user, token


def get_user_by_id(user_id):
    user = User.query.get(int(user_id))
    if not user:
        raise ApiError("User not found", status_code=404)
    return user
