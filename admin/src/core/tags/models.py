from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.associations import tag_historic_site
from core.database import db


class Tag(db.Model):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    deleted: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)

    historic_sites: Mapped[list["HistoricSite"]] = relationship(
        "HistoricSite",
        secondary=tag_historic_site,
        back_populates="tags",
    )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name}>"
