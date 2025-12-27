from enum import Enum

from core.database import db


class Flag(Enum):
    ADMIN_MAINTENANCE_MODE = "admin_maintenance_mode"
    PORTAL_MAINTENANCE_MODE = "portal_maintenance_mode"
    REVIEWS_ENABLED = "reviews_enabled"


class FeatureFlag(db.Model):
    __tablename__ = "feature_flags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    maintenance_message = db.Column(db.String(256), nullable=True)
    modified_by = db.Column(db.String(64), nullable=True)
    modified_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False,
    )

    def __repr__(self):
        """Representación en cadena de un feature flag."""
        return f"<FeatureFlag {self.name}: {self.enabled}>"
