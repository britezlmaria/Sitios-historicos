from dataclasses import dataclass
from typing import Optional

from flask import request, jsonify, Response, Blueprint, current_app
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
from marshmallow import ValidationError
from sqlalchemy import func

from core.auth import repository as user_repo
from core.auth.models import User, user_favorite_sites
from core.database import db
from core.feature_flags import repository as flags_repo
from core.feature_flags.models import Flag
from core.historic_site import repository as hs_repo, prepare_site_data, HistoricSiteSchema, HistoricSiteQuerySchema
from core.historic_site.models import HistoricSite
from core.reviews import ReviewSchema, repository as reviews_repo
from core.reviews.models import Review, ReviewState
from core.tags import repository as tag_repo
from core.tags.models import Tag

bp = Blueprint("api_bp", __name__, url_prefix="/api")


@dataclass
class ApiError:
    code: str
    message: str
    details: Optional[dict[str, list[str]]] = None


@dataclass
class ApiErrorResponse:
    error: ApiError


@bp.get("/sites")
def list_sites() -> tuple[Response, int]:
    """
    Devuelve la lista de sitios historicos paginada
    """
    try:
        try:
            params = HistoricSiteQuerySchema().load(request.args.to_dict())
            only_favorites = request.args.get('only_favorites', 'false').lower() == 'true'
        except ValidationError as err:
            return jsonify({
                "error": {
                    "code": "invalid_query",
                    "message": "Parameter validation failed",
                    "details": err.messages
                }
            }), 400

        # Query base
        query = db.session.query(HistoricSite).filter(HistoricSite.deleted == False)
        
        if only_favorites:
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                query = query.join(user_favorite_sites).filter(
                    user_favorite_sites.c.id_user == current_user_id
                )
            except Exception:
                return jsonify(ApiErrorResponse(
                    ApiError("unauthorized", "You must be logged in to filter by favorites")
                )), 401

        # Filtros de texto
        if params.get("name"):
            query = query.filter(HistoricSite.name.ilike(f"%{params["name"]}%"))
        if params.get("description"):
            query = query.filter(HistoricSite.description.ilike(f"%{params["description"]}%"))
        if params.get("city"):
            query = query.filter(HistoricSite.city.ilike(f"%{params["city"]}%"))
        if params.get("province"):
            query = query.filter(HistoricSite.province.ilike(f"%{params["province"]}%"))
        if params.get("state_of_conservation"):
            query = query.filter(HistoricSite.state_of_conservation == params["state_of_conservation"])

        # Filtro por tags
        if params.get("tags"):
            tag_list = [t.strip() for t in params["tags"].split(",") if t.strip()]
            if tag_list:
                query = query.join(HistoricSite.tags).filter(Tag.name.in_(tag_list))

        # Filtro lat, long, radius
        lat, long, radius = params.get("lat"), params.get("long"), params.get("radius")
        if lat is not None and long is not None and radius is not None:
            # radius en km, PostGIS ST_DWithin usa metros
            radius_m = radius * 1000
            point = func.ST_SetSRID(func.ST_MakePoint(long, lat), 4326)
            query = query.filter(func.ST_DWithin(HistoricSite.location, point, radius_m))

        # Ordenamiento
        order_by = params["order_by"]
        if order_by == "latest":
            query = query.order_by(HistoricSite.inserted_at.desc())
        elif order_by == "oldest":
            query = query.order_by(HistoricSite.inserted_at.asc())
        elif order_by == "rating-5-1":
            query = query.order_by(HistoricSite.rating.desc().nullslast())
        elif order_by == "rating-1-5":
            query = query.order_by(HistoricSite.rating.asc().nullslast())
        elif order_by == "most-visited":
            query = query.order_by(HistoricSite.visit_count.desc())
        elif order_by == "least-visited":
            query = query.order_by(HistoricSite.visit_count.asc())
        else:
            # default
            query = query.order_by(HistoricSite.inserted_at.desc())

        # Retorno paginado
        page = params["page"]
        per_page = params["per_page"]
        return HistoricSite.to_collection_dict(query, page, per_page, 'api_bp.list_sites')
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.post("/sites")
@jwt_required()
def create_site() -> tuple[Response, int]:
    """
    Crea un sitio. Devuelve el sitio creado
    """
    try:
        current_user = get_jwt_identity()
        json = request.get_json() or {}

        try:
            HistoricSiteSchema().load(json)
        except ValidationError as err:
            return jsonify(ApiErrorResponse(
                ApiError("invalid_data", "Invalid data input", err.messages)
            )), 400

        site_data = prepare_site_data(json, tag_repo)
        site = hs_repo.create_historic_site(current_user, **site_data)
        site_dict = site.to_dict()
        return jsonify(site_dict), 201
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.get("/sites/<int:site_id>")
def get_site(site_id: int) -> tuple[Response, int]:
    """
    Obtiene un sitio por id
    """
    try:
        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        hs_repo.increment_visit_count(site_id)
        return site.to_dict()
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500
    
@bp.get("/sites/provinces")
def get_provinces() -> tuple[Response, int]:
    """
    Obtiene todas las provincias registradas 
    """
    try:
        provinces = hs_repo.get_all_provinces()
        return jsonify(provinces), 200
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.post("/auth")
def authenticate() -> tuple[Response, int]:
    """
    Autentica un usuario y le setea la cookie de JWT
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user: User = user_repo.get_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify(ApiErrorResponse(ApiError("invalid_credentials", "Invalid credentials"))), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify()
    set_access_cookies(response, access_token)
    return response, 201

@bp.get("/sites/<int:site_id>/reviews")
def get_all_site_reviews(site_id: int) -> tuple[Response, int]:
    """
    Obtiene todas las reviews de un sitio paginadas
    """
    try:
        page: int = request.args.get("page", 1, type=int)
        per_page: int = request.args.get("per_page", 10, type=int)
        site: HistoricSite = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        query = db.session.query(Review).join(HistoricSite).filter(
            Review.historic_site_id == site.id,
            Review.state == ReviewState.APPROVED,
            Review.deleted == False,
        )

        return Review.to_collection_dict(query, page, per_page, 'api_bp.get_all_site_reviews', site_id=site_id)
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.post("/sites/<int:site_id>/reviews")
@jwt_required()
def add_site_reviews(site_id: int) -> tuple[Response, int]:
    """
    Agrega una review a un sitio
    """
    try:
        if not flags_repo.is_flag_enabled(Flag.REVIEWS_ENABLED):
            return jsonify(ApiErrorResponse(ApiError("service_unavailable", "The reviews are temporary disabled"))), 503

        current_user = get_jwt_identity()
        review_data = request.get_json() or {}
        existing_review = db.session.query(Review).filter_by(
            user_id=current_user, historic_site_id=site_id, deleted=False
        ).first()

        if existing_review:
            return jsonify(ApiErrorResponse(
                ApiError("already_exists", "Ya escribiste una reseña para este sitio")
            )), 400

        comment = review_data.get("comment", "")
        if not (20 <= len(comment) <= 1000):
            return jsonify(ApiErrorResponse(
                ApiError("invalid_data", "The comment must be between 20 and 1000 characters")
            )), 400
        
        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        try:
            ReviewSchema().load(review_data)
        except ValidationError as err:
            return jsonify(ApiErrorResponse(
                ApiError("invalid_data", "Invalid data input", err.messages)
            )), 400

        review = reviews_repo.create_review(
            user_id=current_user,
            site_id=site_id,
            rating=review_data["rating"],
            comment=review_data["comment"]
        )
        return jsonify(review.to_dict()), 201
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.get("/sites/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def get_site_review(site_id: int, review_id: int) -> tuple[Response, int]:
    """
    Obtiene una review de un sitio historico por id
    """
    try:
        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        review = db.session.query(Review).filter(
            Review.id == review_id,
            Review.historic_site_id == site_id,
            Review.deleted == False,
        ).first()

        if not review:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Review not found"))), 404

        if review.state != ReviewState.APPROVED:
            return jsonify(ApiErrorResponse(ApiError("forbidden", "You do not have permission to view this review"))), 403

        return jsonify(review.to_dict()), 200
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.delete("/sites/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def delete_site_review(site_id: int, review_id: int) -> tuple[Response, int]:
    """
    Borra una review de un sitio historico
    """
    try:
        if not flags_repo.is_flag_enabled(Flag.REVIEWS_ENABLED):
            return jsonify(ApiErrorResponse(ApiError("service_unavailable", "The reviews are temporary disabled"))), 503

        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        review = db.session.query(Review).filter(
            Review.id == review_id,
            Review.historic_site_id == site_id,
            Review.deleted == False,
        ).first()

        if not review:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Review not found"))), 404

        if review.state != ReviewState.APPROVED:
            return jsonify(
                ApiErrorResponse(ApiError("forbidden", "You do not have permission to view this review"))), 403

        review.deleted = True
        db.session.commit()
        return jsonify(""), 204
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500


@bp.put("/sites/<int:site_id>/favorite")
@jwt_required()
def favorite_site(site_id: int) -> tuple[Response, int]:
    """
    Agrega el sitio historico como favorito
    """
    try:
        user = user_repo.get_user(get_jwt_identity())
        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        if site in user.favorites:
            return jsonify(""), 204

        user.favorites.append(site)
        db.session.commit()
        return jsonify(""), 204
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected error occurred"))), 418


@bp.delete("/sites/<int:site_id>/favorite")
@jwt_required()
def delete_favorite_site(site_id: int) -> tuple[Response, int]:
    """
    Saca el sitio historico de los favoritos del usuario
    """
    try:
        user = user_repo.get_user(get_jwt_identity())
        site = db.session.query(HistoricSite).filter(HistoricSite.id == site_id, HistoricSite.deleted == False).first()

        if not site or site.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "Site not found"))), 404

        if site not in user.favorites:
            return jsonify(""), 204

        user.favorites.remove(site)
        db.session.commit()
        return jsonify(""), 204
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected error occurred"))), 500


@bp.get("/me/favorites")
@jwt_required()
def list_favorites() -> tuple[Response, int]:
    """
    Obtiene todos los sitios historicos favoritos del usuario
    """
    try:
        user = user_repo.get_user(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        query = db.session.query(HistoricSite).join(user_favorite_sites)\
            .filter(user_favorite_sites.c.id_user == user.id, user_favorite_sites.c.deleted == False)
        return HistoricSite.to_collection_dict(query, page, per_page, 'api_bp.list_favorites')
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected error occurred"))), 500


@bp.get("/me/reviews")
@jwt_required()
def list_reviews_of_user() -> tuple[Response, int]:
    """
    Obtiene todas las reviews del usuario
    """
    try:
        user = user_repo.get_user(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        order_by = request.args.get('order_by', None, type=str)
        query = db.session.query(Review).filter(
            Review.user_id == user.id,
            Review.state == ReviewState.APPROVED,
            Review.deleted == False
        )


        if order_by == "desc":
            query = query.order_by(Review.inserted_at.desc())
        elif order_by == "asc":
            query = query.order_by(Review.inserted_at.asc())

        return Review.to_collection_dict(query, page, per_page, 'api_bp.list_reviews_of_user')
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected error occurred"))), 500


@bp.get("/make_coffee")
def make_coffee() -> tuple[Response, int]:
    return jsonify(ApiErrorResponse(ApiError("im_a_teapot", "I'm a teapot"))), 418

@bp.get("/me")
@jwt_required()
def get_profile() -> tuple[Response, int]:
    """
    Obtiene la información del usuario
    """
    user_id = get_jwt_identity()

    user = user_repo.get_user(user_id)

    if not user:
        return jsonify(ApiErrorResponse(ApiError("not_found", "User not found"))), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar": getattr(user, "avatar", None)
    }), 200

@bp.put("/me")
@jwt_required()
def edit_profile() -> tuple[Response, int]:
    """
    Modifica nombre, apellido y avatar de un usuario
    """
    try:
        current_user = get_jwt_identity()
        user_data = request.get_json() or {}
        user = user_repo.get_user(current_user)

        if not user or user.deleted:
            return jsonify(ApiErrorResponse(ApiError("not_found", "User not found"))), 404

        user = user_repo.update_user(
            current_user,
            **user_data
        )
        return jsonify(user.to_dict()), 201
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500

@bp.post("/logout")
def logout() -> tuple[Response, int]:
    """
    Cierra la sesión del usuario eliminando las cookies JWT.
    """
    response = jsonify({"status": "logged_out"})
    unset_jwt_cookies(response)   
    return response, 200

@bp.get("/flags")
def get_flags() -> tuple[Response, int]:
    """
    Retorna el valor de las flags para que puedan ser llamdas desde el front end
    """
    try:
        portal_maintenance = flags_repo.is_flag_enabled(Flag.PORTAL_MAINTENANCE_MODE)
        portal_maintenance_message = flags_repo.get_maintenance_message(Flag.PORTAL_MAINTENANCE_MODE)
        reviews_enabled = flags_repo.is_flag_enabled(Flag.REVIEWS_ENABLED)

        return jsonify({
            "portal_maintenance": portal_maintenance,
            "portal_maintenance_message": portal_maintenance_message,
            "reviews_enabled": reviews_enabled
        }), 200
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500
    
@bp.get("/tags")
def get_tags() -> tuple[Response, int]:
    """
    Retorna la lista de tags disponibles
    """
    try:
        tags = tag_repo.list_all_tags()
        tags_list = [tag.to_dict() for tag in tags]
        return jsonify(tags_list), 200
    except ValueError:
        return jsonify(ApiErrorResponse(ApiError("server_error", "An unexpected server error occurred"))), 500