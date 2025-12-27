from geoalchemy2 import WKTElement
from marshmallow import Schema, fields, validate, validates, ValidationError

from core.historic_site import repository

class HistoricSiteSchema(Schema):
    name = fields.Str(required=True)
    short_description = fields.Str(required=True)
    description = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    state_of_conservation = fields.Str(required=True)
    inauguration_year = fields.Int(required=True, validate=validate.Range(min=1500, max=2100))
    tags = fields.List(fields.Str(), required=False, allow_none=True)

    @validates("lat")
    def validate_lat(self, value: float, data_key: str) -> None:
        if value is not None and not (-90 <= value <= 90):
            raise ValidationError("Must be a valid latitude")

    @validates("long")
    def validate_long(self, value: float, data_key: str) -> None:
        if value is not None and not (-180 <= value <= 180):
            raise ValidationError("Must be a valid longitude")

from marshmallow import validates, ValidationError, validate

class HistoricSiteQuerySchema(Schema):
    """Schema para validar los parámetros de búsqueda (query params)."""

    name = fields.Str(load_default=None)
    short_description = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    city = fields.Str(load_default=None)
    province = fields.Str(load_default=None)
    lat = fields.Float(load_default=None)
    long = fields.Float(load_default=None)
    radius = fields.Float(load_default=None)
    state_of_conservation = fields.Str(load_default=None)
    inauguration_year = fields.Int(load_default=None, validate=validate.Range(min=1500, max=2100))
    order_by = fields.Str(
        load_default="latest",
        validate=validate.OneOf(["latest", "oldest", "rating-5-1", "rating-1-5", "most-visited", "least-visited"]),
    )
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    state_of_conservation = fields.String(
        required=False, 
        validate=validate.OneOf(["bueno", "regular", "malo"]) 
    )
    tags = fields.Str(load_default=None)
    only_favorites = fields.Boolean(load_default=False)
    
    @validates("lat")
    def validate_lat(self, value: float, data_key: str) -> None:
        if value is not None and not (-90 <= value <= 90):
            raise ValidationError("Must be a valid latitude")

    @validates("long")
    def validate_long(self, value: float, data_key: str) -> None:
        if value is not None and not (-180 <= value <= 180):
            raise ValidationError("Must be a valid longitude")




def prepare_site_data(json: dict, tags_repository) -> dict:
    data = json.copy()

    data["state_of_conservation"] = data["state_of_conservation"].lower()
    data["location"] = WKTElement(f'POINT({data["long"]} {data["lat"]})', srid=4326)
    data.pop("long", None)
    data.pop("lat", None)

    # Convertir tags de strings a modelos
    data["tags"] = tags_repository.get_tags_by_names(data["tags"])
    return data