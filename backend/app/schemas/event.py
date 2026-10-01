from marshmallow import Schema, fields, validate

from app.models.event import VALID_EVENT_TYPES


class EventCreateSchema(Schema):
    session_id = fields.String(required=True, validate=validate.Length(min=1, max=120))
    event_type = fields.String(required=True, validate=validate.OneOf(sorted(VALID_EVENT_TYPES)))
    product_id = fields.Integer(required=False, allow_none=True)
    metadata = fields.Dict(required=False, allow_none=True, data_key="metadata")


event_create_schema = EventCreateSchema()
