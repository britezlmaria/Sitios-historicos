from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core import PaginatedAPIMixin
from core.database import db


class ReviewState(Enum):
    PENDING = "pendiente"
    APPROVED = "aprobada"
    REJECTED = "rechazada"


class Review(db.Model, PaginatedAPIMixin):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[str] = mapped_column(String, nullable=False)
    inserted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
    state: Mapped[ReviewState] = mapped_column(
        SAEnum(ReviewState, name="review_state_enum"),
        nullable=False,
        default=ReviewState.PENDING
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    rejected_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    historic_site_id: Mapped[int] = mapped_column(Integer, ForeignKey("historic_site.id"), nullable=False)

    user = relationship("User", back_populates="reviews")
    historic_site = relationship("HistoricSite", back_populates="reviews")

    def to_dict(self) -> dict:
        """Convierte el objeto Review a un diccionario."""
        user_name = f"{self.user.name} {self.user.last_name}" if self.user else "Unknown"
        return {
            "id": self.id,
            "historic_site_id": self.historic_site_id,
            "rating": self.rating,
            "comment": self.comment,
            "inserted_at": self.inserted_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "state": self.state.value,
            "user_id": self.user_id,
            "user_name": user_name,
        }

    def __repr__(self):
        return f"<Review id={self.id} state={self.state}>"