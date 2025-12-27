from core import db
from core.reviews.models import Review, ReviewState
from core.auth.models import User
from datetime import datetime

def list_reviews() -> list[Review]:
    """Obtiene todas las reviews

    Returns:
        list[Review]: lista con todas las reviews
    """
    return db.session.query(Review).order_by(Review.created_at.desc()).all()

def get_review_by_id(review_id: int) -> Review | None:
    """Obtiene una review por su ID

    Args:
        review_id (int): ID de la review

    Returns:
        Review | None: review encontrada o None si no existe
    """
    return db.session.query(Review).filter(Review.id == review_id).first()

def reviews_paginated(site_id: int|None , page: int,rating: int|None , state: str = "", date: str = "", user: str = "", order: str = "recientes") -> list[Review]:
    """obtiene todas las rewiews de un sitio historico especifico

    Args:
        site_id (int): id del sitio historico
        page (int): pagina actual
        state (str, optional): estado de la review. Defaults to "".
        date (str, optional): rango de fechas. Defaults to "".
        user (str, optional): usuario que hizo la review. Defaults to "".
        order (str, optional): orden de las reviews. Defaults to "recientes".

    Returns:
        list[Review]: reviews del sitio historico
    """
    query = db.session.query(Review)
    if site_id:
        query = query.filter(Review.historic_site_id == site_id)
    if state:
        state_enum = ReviewState(state)
        query = query.filter(Review.state == state_enum)
    if rating is not None:
        query = query.filter(Review.rating == rating)
    if date:
        fechas = date.split(" a ")
        if len(fechas) == 2:
            fecha_inicio = datetime.strptime(fechas[0], "%Y-%m-%d")
            fecha_fin = datetime.strptime(fechas[1], "%Y-%m-%d")
            query = query.filter(Review.inserted_at.between(fecha_inicio, fecha_fin))
    if user:
        query = query.join(User).filter(Review.user.has(db.or_(db.func.lower(User.email).like(f"%{user.lower()}%"), db.func.lower(User.name).like(f"%{user.lower()}%"))))
    
    query = query.order_by(None)

    if order == "recientes":
        query = query.order_by(Review.inserted_at.desc())
    elif order == "antiguas":
        query = query.order_by(Review.inserted_at.asc())
    elif order == "mejor calificadas":
        query = query.order_by(Review.rating.desc())
    elif order == "peor calificadas":
        query = query.order_by(Review.rating.asc())
    query = query.filter(Review.deleted == False)
    return db.paginate(query, per_page=25, page=page, error_out=False)

def aprove_review(review: Review) -> Review:
    """Aprueba una review

    Args:
        review (Review): review a aprobar

    Returns:
        Review: review aprobada
    """
    review.state = ReviewState.APPROVED
    review.rejected_reason = None
    db.session.commit()
    return review

def reject_review(review: Review, reason: str) -> Review:
    """Rechaza una review

    Args:
        review (Review): review a rechazar
        reason (str): motivo del rechazo

    Returns:
        Review: review rechazada
    """
    if not reason:
        raise ValueError("Se debe proporcionar un motivo para rechazar la reseña.")
    if len(reason) > 200:
        raise ValueError("El motivo de rechazo no puede exceder los 200 caracteres.")
    if review.state == ReviewState.REJECTED:
        raise ValueError("La reseña ya ha sido rechazada previamente.")
    review.state = ReviewState.REJECTED
    review.rejected_reason = reason
    db.session.commit()
    return review

def delete_review_db(review: Review) -> None:
    """Elimina una review

    Args:
        review (Review): review a eliminar
    """
    review.deleted = True
    db.session.commit()

def create_review(user_id, site_id, rating, comment, visible=True):
    review = Review(
        user_id=user_id,
        historic_site_id=site_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    return review