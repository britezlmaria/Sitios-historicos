from marshmallow import Schema, fields, validate


class ReviewSchema(Schema):
    historic_site_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(required=False, allow_none=True)

