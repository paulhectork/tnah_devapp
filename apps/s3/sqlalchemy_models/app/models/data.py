from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.app import db


# comment lit-on chacun des attributs ci-dessous ?
class Iconography(db.Model):
    __tablename__ = "Iconography"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    iiif_manifest_url: Mapped[str]
    iiif_image_url: Mapped[str]
    source_url: Mapped[Optional[str]]
    richelieu_url: Mapped[str]
    date_lower: Mapped[Optional[int]]
    date_upper: Mapped[Optional[int]]
    institution: Mapped[int]
    # NOTE: il reste à définir la relation avec la table `author`, mais on verra comment faire plus tard !
    id_author = ...
