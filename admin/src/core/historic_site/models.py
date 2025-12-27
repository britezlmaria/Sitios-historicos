from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geometry
from shapely.geometry import Point
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from sqlalchemy.sql import func, select, expression

from core import PaginatedAPIMixin
from core.associations import tag_historic_site
from core.database import db
from core.reviews.models import Review


class HistoricSite(db.Model, PaginatedAPIMixin):
    __tablename__ = "historic_site"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[Point] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    state_of_conservation: Mapped[str] = mapped_column(
        ENUM("bueno", "regular", "malo", name="state_of_conservation_enum"), nullable=False
    )
    inauguration_year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[list["Category"]] = relationship(
        secondary="category_historic_site"
    )
    visible: Mapped[bool] = mapped_column(Boolean, default=False)
    modifications: Mapped[list["Modification"]] = relationship(backref="historic_site")
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    tags: Mapped[list["Tag"]] = relationship(
        secondary=tag_historic_site,
        back_populates="historic_sites",
    )

    reviews: Mapped[list["Review"]] = relationship(back_populates="historic_site",cascade="all, delete-orphan")
    rating = column_property( select(func.avg(Review.rating))
                             .where(Review.historic_site_id == id)
                             .correlate_except(Review)
                             .scalar_subquery() 
    )

    visit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index(
            "unique_active_name",  # nombre del índice
            "name",  # columna
            unique=True,
            postgresql_where=expression.false() == expression.column("deleted"),
        ),
    )

    images: Mapped[list["Image"]] = relationship(
        back_populates="historic_site",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    inserted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    @property
    def lat(self) -> float:
        """Devuelve la latitud del punto"""
        if self.location:
            point = to_shape(self.location)
            return point.y  # latitude
        return None

    @property
    def lon(self) -> float:
        """Devuelve la longitud del punto"""
        if self.location:
            point = to_shape(self.location)
            return point.x  # longitude
        return None
    
    def to_dict(self) -> dict:
        """Convierte el objeto sitio histórico a un diccionario"""
        images_list = [
            img.to_dict() for img in self.active_images
        ]
        return {
            "id": self.id,
            "name": self.name,
            "short_description": self.short_description,
            "description": self.description,
            "city": self.city,
            "province": self.province,
            "lat": self.lat,
            "long": self.lon,
            "state_of_conservation": self.state_of_conservation,
            "inauguration_year": self.inauguration_year,
            "category": [cat.name for cat in self.category],
            "tags": [tag.name for tag in self.tags],
            "inserted_at": self.inserted_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.modifications[0].id_user,
            "rating": float(self.rating) if self.rating is not None else None,
            "reviews":[review.to_dict() for review in self.reviews if not review.deleted],
            "visit_count": self.visit_count,
            "cover_image": {
                "url": self.cover_image.image,
                "title": self.cover_image.title
            } if self.cover_image else None,
            "images_list": images_list,
            # "visible": self.visible, # TODO: Preguntar si el sitio no esta visible deberia devolverlo la api
        }
        
    @property
    def cover_image(self):
        """Devuelve la imagen marcada como portada, o la primera"""
        cover = next((img for img in self.images if img.is_cover and not img.deleted), None)
        if cover:
            return cover
        # Si no hay portada, devolver la primera
        for img in self.images:
            if not img.deleted:
                return img
        return None
    
    @property
    def active_images(self):
        """Devuelve las imágenes activas ordenadas por order_index"""
        return sorted(
            [img for img in self.images if not img.deleted],
            key=lambda x: x.order_index
        )


category_historic_site = db.Table(
    "category_historic_site",
    db.metadata,
    db.Column(
        "id_historic_site",
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "id_category",
        db.Integer,
        db.ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("deleted", db.Boolean, default=False),
)


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class Image(db.Model):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_historic_site: Mapped[int] = mapped_column(
        ForeignKey("historic_site.id", ondelete="CASCADE"), nullable=False
    )
    historic_site: Mapped["HistoricSite"] = relationship(back_populates="images")
    
    
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)        
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)   
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadatos
    content_type: Mapped[str | None] = mapped_column(String(50))
    size: Mapped[int | None] = mapped_column(Integer)
    
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    
    def to_dict(self) -> dict:
        """Convierte el objeto imagen a un diccionario"""
        return {
            "id": self.id,
            "image": self.image,
            "title": self.title,
            "description": self.description,
            "order_index": self.order_index,
            "is_cover": self.is_cover,
            "content_type": self.content_type,
            "size": self.size,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class Modification(db.Model):
    __tablename__ = "modification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
    )
    type: Mapped[list["ModificationType"]] = relationship(
        secondary="modification_modification_type"
    )
    id_historic_site: Mapped[int] = mapped_column(
        ForeignKey("historic_site.id"), nullable=False
    )
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)


modification_modification_type = db.Table(
    "modification_modification_type",
    db.metadata,
    db.Column(
        "id_modification",
        db.Integer,
        db.ForeignKey("modification.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "id_modification_type",
        db.Integer,
        db.ForeignKey("modification_type.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("deleted", db.Boolean, default=False),
)


class ModificationType(db.Model):
    __tablename__ = "modification_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        ENUM(
            "Creación",
            "Edición",
            "Eliminación",
            "Cambio de estado",
            "Cambio de tags",
            name="modification_type_enum",
        ),
        nullable=False,
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
