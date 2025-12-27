from datetime import UTC, datetime, timedelta

from core.database import db
from core.feature_flags.models import FeatureFlag, Flag


def get_all_flags():
    """Retorna todos los feature flags."""
    return FeatureFlag.query.all()


def get_flag_by_enum(enum: Flag):
    """Retorna un feature flag por su nombre."""
    return FeatureFlag.query.filter_by(name=enum.value).first()


def create_flag(**data):
    """Crea un nuevo feature flag."""
    flag = FeatureFlag(**data)
    db.session.add(flag)
    db.session.commit()
    return flag


def update_flag(flag_id, enabled, modified_by=None, maintenance_message=None):
    """Actualiza un feature flag existente."""
    flag = FeatureFlag.query.get(flag_id)
    if flag:
        flag.enabled = enabled
        if modified_by:
            flag.modified_by = modified_by
        flag.modified_at = datetime.now(UTC) - timedelta(hours=3)
        if maintenance_message is not None:
            flag.maintenance_message = maintenance_message
        db.session.commit()
    return flag


def is_flag_enabled(value: Flag):
    """Verifica si un feature flag está habilitado."""
    flag = get_flag_by_enum(value)
    return flag.enabled if flag else False


def get_maintenance_message(value: Flag):
    """Obtiene el mensaje de mantenimiento de un feature flag si está habilitado."""
    flag = get_flag_by_enum(value)
    return flag.maintenance_message if flag and flag.enabled else None


def get_flag_by_id(flag_id):
    """Retorna un feature flag por su ID."""
    return FeatureFlag.query.get(flag_id)
