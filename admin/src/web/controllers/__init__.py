from functools import wraps

from flask import abort, flash, redirect, render_template, session, url_for

from core.auth import repository
from core.feature_flags.models import Flag
from core.feature_flags.repository import get_maintenance_message, is_flag_enabled


def permission_required(permission_name):
    """
    Decorador que verifica si el usuario actual tiene el permiso requerido.

    - Si el usuario no está logueado, lo redirige al login.
    - Si el usuario no existe, no está habilitado o no tiene el permiso, aborta con error 401.
    - Si todo es correcto, ejecuta la función decorada pasando el usuario como argumento 'current_user'.

    Parámetros:
        permission_name (str): Nombre del permiso requerido.

    Retorna:
        function: La función decorada que solo se ejecuta si el usuario tiene el permiso.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")

            if not user_id:
                return redirect(url_for("auth_bp.login"))
            user = repository.get_user(user_id)
            try:
                if not user:
                    raise ValueError("El usuario no existe")
                if not user.enabled:
                    raise ValueError("El usuario no se encuentra habilitado")
                if not repository.has_permission(user, permission_name):
                    raise ValueError("El usuario no se encuentra habilitado")
            except ValueError:
                abort(401)
            return f(current_user=user, *args, **kwargs)

        return wrapper

    return decorator


def success_message(message: str) -> None:
    flash(message, "success")


def error_message(message: str) -> None:
    flash(message, "error")


def info_message(message: str) -> None:
    flash(message, "info")


def warning_message(message: str) -> None:
    flash(message, "warning")


def admin_maintenance_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si el modo mantenimiento está activado
        if is_flag_enabled(Flag.ADMIN_MAINTENANCE_MODE):
            # Obtener el usuario actual
            current_user = repository.get_user(session.get("user_id"))

            # Si hay usuario y es system admin
            if current_user and current_user.system_admin:
                # Verificar si está intentando acceder a feature flags
                from flask import request

                # Permitir acceso solo a rutas de feature flags
                if "/feature-flags" in request.path:
                    return f(*args, **kwargs)
                else:
                    # System admin intentando acceder a otra funcionalidad
                    maintenance_message = get_maintenance_message(
                        Flag.ADMIN_MAINTENANCE_MODE
                    )
                    return render_template(
                        "feature_flags/maintenance.html",
                        message=maintenance_message,
                        user=current_user,
                    )

            # Usuario logueado que NO es system admin intentando acceder a rutas protegidas
            if current_user and not current_user.system_admin:
                maintenance_message = get_maintenance_message(Flag.ADMIN_MAINTENANCE_MODE)
                return render_template(
                    "feature_flags/maintenance.html",
                    message=maintenance_message,
                    user=current_user,
                )

            # Si no hay usuario logueado, redirigir al login
            return redirect(url_for("auth_bp.login"))

        return f(*args, **kwargs)

    return decorated_function
