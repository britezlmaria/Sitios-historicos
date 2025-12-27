from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.auth import repository
from core.feature_flags.repository import get_all_flags, get_flag_by_id, update_flag

feature_flags_bp = Blueprint("feature_flags", __name__, url_prefix="/feature-flags")


def is_system_admin():
    """Verifica si el usuario actual es system admin."""
    current_user = repository.get_user(session.get("user_id"))
    return current_user and current_user.system_admin


@feature_flags_bp.route("/", methods=["GET"])
def panel():
    """Muestra el panel de administración de feature flags."""
    if not is_system_admin():
        abort(401)

    current_user = repository.get_user(session.get("user_id"))
    flags = get_all_flags()
    return render_template(
        "feature_flags/feature_flags.html", flags=flags, user=current_user
    )


@feature_flags_bp.route("/update/<int:flag_id>", methods=["POST"])
def update(flag_id):
    """Actualiza el estado de un feature flag."""
    if not is_system_admin():
        abort(401)

    enabled = request.form.get("enabled") == "on"
    message = request.form.get("maintenance_message", "")

    flag = get_flag_by_id(flag_id)
    if not flag:
        flash("Feature flag no encontrado.", "danger")
        return redirect(url_for("feature_flags.panel"))

    is_maintenance_flag = "_maintenance_mode" in flag.name

    # Solo validar mensaje si es flag de mantenimiento y está siendo activado
    if is_maintenance_flag and enabled and (not message or message.strip() == ""):
        flash(
            "El mensaje de mantenimiento es obligatorio cuando se activa el modo mantenimiento.",
            "danger",
        )
        return redirect(url_for("feature_flags.panel"))

    # Validar longitud máxima
    if message and len(message) > 256:
        flash(
            "El mensaje de mantenimiento no puede exceder los 256 caracteres.", "danger"
        )
        return redirect(url_for("feature_flags.panel"))

    # Obtener información del usuario actual para la auditoría
    current_user = repository.get_user(session.get("user_id"))
    modified_by = current_user.email if current_user else "system"

    # Actualizar el flag
    update_flag(flag_id, enabled, modified_by, message)

    action = "activado" if enabled else "desactivado"
    flash(f"Flag {action} correctamente.", "success")
    return redirect(url_for("feature_flags.panel"))
