from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)
    category = fields.String(required=False, allow_none=True, validate=validate.Length(max=120))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    stock = fields.Integer(required=False, load_default=0, validate=validate.Range(min=0))
    image_url = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))


class ProductUpdateSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)
    category = fields.String(required=False, allow_none=True, validate=validate.Length(max=120))
    price = fields.Decimal(required=False, places=2, validate=validate.Range(min=0))
    stock = fields.Integer(required=False, validate=validate.Range(min=0))
    image_url = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))


product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
