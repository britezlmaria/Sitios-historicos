from flask import Blueprint, redirect, render_template, request, session

from core.auth.models import User
from core.auth.repository import get_user_by_email
from core.feature_flags.models import Flag
from core.feature_flags.repository import get_maintenance_message, is_flag_enabled
from web.controllers import success_message

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login():
    """Renderiza la página de inicio de sesión"""
    # Verificar si el modo mantenimiento está activo
    maintenance_mode = is_flag_enabled(Flag.ADMIN_MAINTENANCE_MODE)
    maintenance_message = (
        get_maintenance_message(Flag.ADMIN_MAINTENANCE_MODE) if maintenance_mode else None
    )

    return render_template(
        "auth/login.html",
        maintenance_mode=maintenance_mode,
        maintenance_message=maintenance_message,
    )


@auth_bp.post("/login")
def authenticate():
    """Maneja el proceso de inicio de sesión de los usuarios"""
    email: str = request.form.get("email")
    password: str = request.form.get("password")

    user: User = get_user_by_email(email)
    if not user or not user.check_password(password):
        return render_template(
            "auth/login.html",
            error="Email o contraseña incorrectos",
            form={"email": email},
        )

    # Crear la sesion
    session["user_id"] = user.id
    success_message("Has iniciado sesión correctamente.")
    return redirect("/")


@auth_bp.get("/logout")
def logout():
    """Maneja el cierre de sesión de los usuarios"""
    session["user_id"] = None
    success_message("Has cerrado sesión correctamente.")
    return redirect("/")
