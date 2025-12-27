from flask import Blueprint, redirect, render_template, request, url_for

from core.tags import repository
from web.controllers import (
    admin_maintenance_check,
    permission_required,
    success_message,
)

tags_bp = Blueprint("tags_bp", __name__, url_prefix="/tags")


@tags_bp.route("/list")
@permission_required("tags_management")
@admin_maintenance_check
def list_tags(current_user=None):
    """
    Muestra la lista de tags con paginacion, busqueda y ordenamiento

    Args:
        current_user (User, optional): Usuario actual

    Returns:
        Response: Página HTML renderizada que muestra la lista de etiquetas
    """
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    order = request.args.get("order", "recientes", type=str)
    error = request.args.get("error")

    tags, total_pages = repository.list_tags(page=page, search=search, order=order)

    return render_template(
        "tags/list_tags.html",
        tags=tags,
        page=page,
        total_pages=total_pages,
        search=search,
        order=order,
        error=error,
        user=current_user,
    )


@tags_bp.route("/create", methods=["GET", "POST"])
@permission_required("tags_management")
@admin_maintenance_check
def create(current_user=None):
    """
    Crea una nueva etiqueta en el sistema

    Args:
        current_user (User, optional): Usuario actual

    Returns:
        Response: Página HTML renderizada para crear una nueva etiqueta o redirige a la lista de etiquetas despues de la creacion
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            repository.create_tag(name)
            success_message("Etiqueta creada correctamente.")
            return redirect(url_for("tags_bp.list_tags"))
        except ValueError as e:
            return render_template(
                "tags/create_tag.html", error=str(e), form={"name": name}
            )

    return render_template("tags/create_tag.html", user=current_user)


@tags_bp.route("/update", methods=["GET", "POST"])
@permission_required("tags_management")
@admin_maintenance_check
def update(current_user=None):
    """
    Actualiza una etiqueta existente

    Args:
        current_user (User, optional): usuario actual

    Returns:
        Response: Página HTML renderizada para actualizar una etiqueta o redirige a la lista de etiquetas despues de la actualizacion
    """
    tag_id = request.args.get("id", type=int) or request.form.get("id", type=int)
    if not tag_id:
        return redirect(url_for("tags_bp.list_tags"))

    tag = repository.get_tag_by_id(tag_id)
    if not tag:
        return redirect(url_for("tags_bp.list_tags"))
    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        try:
            repository.update_tag(tag_id, new_name)
            success_message("Etiqueta actualizada correctamente.")
            return redirect(url_for("tags_bp.list_tags"))
        except ValueError as e:
            return render_template("tags/update_tag.html", error=str(e), tag=tag)

    return render_template("tags/update_tag.html", tag=tag, user=current_user)


@tags_bp.route("/delete", methods=["POST"])
@permission_required("tags_management")
@admin_maintenance_check
def delete(current_user=None):
    """
    Elimina una etiqueta seleccionada

    Args:
        current_user (User, optional): usuario actual

    Returns:
        Response: Redirige a la lista de etiquetas despues de la eliminacion
    """
    tag_id = request.args.get("id", type=int) or request.form.get("id", type=int)
    if not tag_id:
        return redirect(url_for("tags_bp.list_tags"))
    try:
        repository.delete_tag(tag_id)
        success_message("Etiqueta eliminada correctamente.")
    except ValueError as e:
        return redirect(url_for("tags_bp.list_tags", error=str(e)))

    return redirect(url_for("tags_bp.list_tags"))
