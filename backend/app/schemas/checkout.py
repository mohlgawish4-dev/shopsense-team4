from marshmallow import Schema, fields


class CheckoutSchema(Schema):
    # Checkout operates on the authenticated user's current cart, so no
    # required fields today. session_id is accepted so the resulting
    # "purchase" event can be tied to the same browsing session.
    session_id = fields.String(required=False, allow_none=True)


checkout_schema = CheckoutSchema()
