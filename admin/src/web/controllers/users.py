from flask import Blueprint, redirect, render_template, request, url_for

from core import auth
from core.auth import repository
from web.controllers import (
    admin_maintenance_check,
    error_message,
    permission_required,
    success_message,
)

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")
# CRUD


# listar usuarios
@user_bp.route("/list", methods=["GET"])
@permission_required("user_index")
@admin_maintenance_check
def list(current_user=None):
    """
    Muestra el listado de usuarios con filtros y paginación.

    Parámetros:
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Renderiza la plantilla 'users/list.html' con los usuarios y roles.
    """
    page = int(request.args.get("page", 1))
    email = request.args.get("email")
    enabled = request.args.get("enabled")
    role_name = request.args.get("role")
    order_by_date = request.args.get("order_by_date", "asc")

    users = repository.search_users(
        email=email,
        enabled=True if enabled == "SI" else False if enabled == "NO" else None,
        role_name=role_name,
        order_by_date=order_by_date,
        page=page,
        per_page=25,
    )

    roles = repository.list_roles()

    return render_template(
        "users/list.html", user=current_user, users=users, page=page, roles=roles
    )


# crear usuarios
@user_bp.route("/create", methods=["GET", "POST"])
@permission_required("user_new")
@admin_maintenance_check
def create(current_user=None):
    """
    Permite crear un nuevo usuario.

    Si el método es POST, valida y crea el usuario, mostrando errores campo a campo si corresponde.
    Si es GET, muestra el formulario vacío.

    Parámetros:
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Renderiza la plantilla 'users/create.html' o redirige al listado.
    """
    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "name": request.form.get("name"),
            "last_name": request.form.get("last_name"),
            "password": request.form.get("password"),
            "enabled": True if request.form.get("enabled") == "SI" else False,
            "id_role": (
                int(request.form.get("id_role"))
                if request.form.get("id_role")
                else None
            ),
        }
        try:
            auth.create_user(**data)
            success_message("Usuario creado correctamente.")
            return redirect(url_for("user_bp.list"))
        except ValueError as e:
            errors = e.args[0]
            roles = repository.list_roles()
            return render_template(
                "users/create.html",
                user=current_user,
                errors=errors,
                form=data,
                roles=roles,
            )

    roles = repository.list_roles()
    return render_template("users/create.html", user=current_user, roles=roles)


# editar usuarios
@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@permission_required("user_update")
@admin_maintenance_check
def update(user_id, current_user=None):
    """
    Permite editar los datos de un usuario existente.

    Si el método es POST, valida y actualiza el usuario, mostrando errores campo a campo si corresponde.
    Si es GET, muestra el formulario con los datos actuales.

    Parámetros:
        user_id (int): ID del usuario a editar.
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Renderiza la plantilla 'users/update.html' o redirige al listado.
    """
    user = repository.get_user(user_id)
    if not user:
        error_message("El usuario que intentás editar no existe.")
        return redirect(url_for("user_bp.list"))

    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "name": request.form.get("name"),
            "last_name": request.form.get("last_name"),
            "password": request.form.get("password"),
            "enabled": True if request.form.get("enabled") == "SI" else False,
            "id_role": (
                int(request.form.get("id_role"))
                if request.form.get("id_role")
                else None
            ),
        }
        try:
            auth.update_user(user_id, **data)
            success_message("Usuario actualizado correctamente.")
            return redirect(url_for("user_bp.list"))
        except ValueError as e:
            errors = e.args[0]
            roles = repository.list_roles()
            return render_template(
                "users/update.html",
                user=current_user,
                errors=errors,
                form=data,
                editing_user=user,
                roles=roles,
            )

    roles = repository.list_roles()
    return render_template(
        "users/update.html", user=current_user, editing_user=user, roles=roles
    )


# eliminar usuarios
@user_bp.route("/delete/<int:user_id>", methods=["POST"])
@permission_required("user_destroy")
@admin_maintenance_check
def delete(user_id, current_user=None):
    """
    Elimina (marca como eliminado) un usuario.

    No permite eliminar el propio usuario ni administradores.

    Parámetros:
        user_id (int): ID del usuario a eliminar.
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Redirige al listado de usuarios.
    """
    if user_id == current_user.id:
        error_message("No podes eliminar tu propio usuario.")
        return redirect(url_for("user_bp.list"))
    try:
        repository.delete_user(user_id)
        success_message("Usuario eliminado correctamente.")
    except ValueError as e:
        error_message(str(e))

    return redirect(url_for("user_bp.list"))


@user_bp.route("/view_detail/<int:user_id>", methods=["GET"])
@permission_required("user_show")
def view_detail(user_id, current_user=None):
    """
    Muestra el detalle de un usuario.

    Parámetros:
        user_id (int): ID del usuario a mostrar.
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Renderiza la plantilla 'users/view_detail.html' o redirige al listado.
    """
    user = repository.get_user(user_id)
    if not user:
        return redirect(url_for("user_bp.list"))
    return render_template(
        "users/view_detail.html", user=current_user, detail_user=user
    )


# bloquear usuario
@user_bp.route("/block/<int:user_id>", methods=["POST"])
@permission_required("block_user")
@admin_maintenance_check
def block(user_id, current_user=None):
    """
    Bloquea (deshabilita) un usuario, excepto a sí mismo y administradores.

    Parámetros:
        user_id (int): ID del usuario a bloquear.
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Redirige al listado de usuarios.
    """
    if user_id == current_user.id:
        error_message("No podés bloquear tu propio usuario.")
        return redirect(url_for("user_bp.list"))
    try:
        repository.block_user(user_id)
        success_message("Usuario bloqueado con exito.")
    except ValueError as e:
        error_message(str(e))
    return redirect(url_for("user_bp.list"))


@user_bp.route("/unblock/<int:user_id>", methods=["POST"])
@permission_required("unblock_user")
@admin_maintenance_check
def unblock(user_id, current_user=None):
    """
    Desbloquea (habilita) un usuario.

    Parámetros:
        user_id (int): ID del usuario a desbloquear.
        current_user (User, opcional): Usuario autenticado.

    Retorna:
        Redirige al listado de usuarios.
    """
    repository.unblock_user(user_id)
    success_message("Usuario desbloqueado con éxito.")
    return redirect(url_for("user_bp.list"))
