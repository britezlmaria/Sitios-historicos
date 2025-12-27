from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.database import db
from core.encription import bcrypt

user_favorite_sites = db.Table(
    "user_favorite_sites",
    db.metadata,
    db.Column(
        "id_user",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "id_historic_site",
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("deleted", db.Boolean, default=False),
)


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    system_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    id_role: Mapped[int] = mapped_column(ForeignKey("role.id_role"), nullable=False)
    role: Mapped["Role"] = relationship(back_populates="users")
    inserted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=db.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    modifications: Mapped[list["Modification"]] = relationship(backref="user")
    favorites: Mapped[list["HistoricSite"]] = relationship(secondary=user_favorite_sites)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)


    # índice único solo si deleted = false
    # Esto permite tener múltiples registros con el mismo email si están marcados como eliminados
    __table_args__ = (
        Index(
            "unique_active_email",  # nombre del índice
            "email",  # columna
            unique=True,
            postgresql_where=expression.false() == expression.column("deleted"),
        ),
    )

    def set_password(self, password: str):
        """Genera un hash seguro para la contraseña y lo asigna al usuario"""
        self.password = bcrypt.generate_password_hash(password.encode("utf-8")).decode(
            "utf-8"
        )

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        return bcrypt.check_password_hash(
            self.password.encode("utf-8"), password.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name,
            "avatar": self.avatar,
            "inserted_at": self.inserted_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name}, last_name={self.last_name})>"


class Role(db.Model):
    __tablename__ = "role"
    id_role: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")
    role_permissions: Mapped[list["Role_Permission"]] = relationship(
        back_populates="role"
    )

    def __repr__(self):
        return f"<Role(id_role={self.id_role}, name={self.name})>"


class Role_Permission(db.Model):
    __tablename__ = "role_permissions"
    id_role: Mapped[int] = mapped_column(ForeignKey("role.id_role"), primary_key=True)
    id_permission: Mapped[int] = mapped_column(
        ForeignKey("permission.id_permission"), primary_key=True
    )

    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")

    def __repr__(self):
        return f"<Role_Permission(id_role={self.id_role}, id_permission={self.id_permission})>"


class Permission(db.Model):
    __tablename__ = "permission"
    id_permission: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    role_permissions: Mapped[list["Role_Permission"]] = relationship(
        back_populates="permission"
    )

    def __repr__(self):
        return f"<Permission(id_permission={self.id_permission}, name={self.name})>"
