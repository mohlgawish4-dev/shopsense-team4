from marshmallow import Schema, fields, validate


class AddCartItemSchema(Schema):
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1))


class UpdateCartItemSchema(Schema):
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))


add_cart_item_schema = AddCartItemSchema()
update_cart_item_schema = UpdateCartItemSchema()
