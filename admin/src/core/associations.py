from sqlalchemy import Column, ForeignKey, Integer, Table

from core.database import db

tag_historic_site = Table(
    "tag_historic_site",
    db.metadata,
    Column(
        "id_historic_site",
        Integer,
        ForeignKey("historic_site.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_tag", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
)
