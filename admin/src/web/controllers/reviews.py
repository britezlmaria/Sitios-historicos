from flask import Blueprint, redirect, render_template, request, url_for

from core.reviews import repository
from core.historic_site import repository as historic_sites_repository
from web.controllers import (
    admin_maintenance_check,
    permission_required,
    success_message,
    error_message
)

reviews_bp = Blueprint("reviews_bp", __name__, url_prefix="/reviews")

@reviews_bp.route("/list")
@permission_required("reviews_management")
@admin_maintenance_check
def list_reviews(current_user=None):
    """
    Muestra la lista de reviews con paginacion, busqueda y ordenamiento

    Args:
        current_user (User, optional): Usuario actual

    Returns:
        Response: Página HTML renderizada que muestra la lista de reviews
    """
    page = request.args.get("page", 1)
    site_id = request.args.get("site_id","")
    state = request.args.get("state", "")
    rating = request.args.get("rating", type=int)
    date = request.args.get("fecha_rango", "")
    user = request.args.get("search_user", "")
    order = request.args.get("order", "recientes")

    pagination = repository.reviews_paginated(
        site_id=site_id,
        page=page,
        state=state,
        rating=rating,
        date=date,
        user=user,
        order=order
    )
    reviews = pagination.items
    total_pages = pagination.pages

    sites = historic_sites_repository.list_historic_sites()

    return render_template(
        "reviews/list_reviews.html",
        reviews=reviews,
        page=page,
        total_pages=total_pages,
        site_id=site_id,
        state=state,
        rating=rating,
        date=date,
        search_user=user,
        order=order,
        user=current_user,
        sites=sites
    )

@reviews_bp.route("/view/<int:review_id>", methods=["GET"])
@permission_required("reviews_management")
@admin_maintenance_check
def view_review(review_id: int, current_user=None):
    """Muestra los detalles de una review

    Args:
        review_id (int): ID de la review
        current_user (_type_, optional): Usuario actual. Defaults to None.
    """

    review = repository.get_review_by_id(review_id)
    return render_template(
        "reviews/view_review.html",
        review=review,
        user=current_user
    )

@reviews_bp.route("/approve/<int:review_id>", methods=["POST"])
@permission_required("reviews_management")
@admin_maintenance_check
def approve_review(review_id: int, current_user=None):
    """Aprueba una review

    Args:
        review_id (int): ID de la review
        current_user (_type_, optional): Usuario actual. Defaults to None.
    """
    review = repository.get_review_by_id(review_id)
    repository.aprove_review(review)
    success_message("Reseña aprobada correctamente")
    return redirect(
        url_for(
            "reviews_bp.list_reviews",
        )
    )

@reviews_bp.route("/reject/<int:review_id>", methods=["POST"])
@permission_required("reviews_management")
@admin_maintenance_check
def reject_review(review_id: int, current_user=None):
    """Rechaza una review

    Args:
        review_id (int): ID de la review
        current_user (_type_, optional): Usuario actual. Defaults to None.
    """
    try:
        reason = request.form.get("reason", "").strip()
        review = repository.get_review_by_id(review_id)
        repository.reject_review(review, reason)
        success_message("Reseña rechazada correctamente")
        return redirect(
            url_for(
                "reviews_bp.list_reviews",
            )
        )
    except ValueError as e:
        error_message(str(e))
        return redirect(
            url_for(
                "reviews_bp.list_reviews"
            )
        )


@reviews_bp.route("/delete/<int:review_id>", methods=["POST"])
@permission_required("reviews_management")
@admin_maintenance_check
def delete_review(review_id: int, current_user=None):
    """Elimina una review

    Args:
        review_id (int): ID de la review
        current_user (_type_, optional): Usuario actual. Defaults to None.
    """
    review = repository.get_review_by_id(review_id)
    repository.delete_review_db(review)
    success_message("Reseña eliminada correctamente")
    return redirect(
        url_for(
            "reviews_bp.list_reviews",
        )
    )
    