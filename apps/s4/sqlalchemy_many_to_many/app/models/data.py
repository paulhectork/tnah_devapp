from typing import Optional, List, Dict

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.app import db



class IconographyPlace(db.Model):
    __tablename__ = "iconography_place"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_iconography: Mapped[int] = mapped_column(ForeignKey("iconography.id"))
    id_place: Mapped[int] = mapped_column(ForeignKey("place.id"))


class IconographyTheme(db.Model):
    __tablename__ = "iconography_theme"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_iconography: Mapped[int] = mapped_column(ForeignKey("iconography.id"))
    id_theme: Mapped[int] = mapped_column(ForeignKey("theme.id"))


class Author(db.Model):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_name: Mapped[str] = mapped_column(unique=True)

    iconography: Mapped[List["Iconography"]] = relationship(
        back_populates="author", 
    )


class Theme(db.Model):
    __tablename__ = "theme"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_name: Mapped[str] = mapped_column(unique=True)
    richelieu_url: Mapped[str] = mapped_column(unique=True)

    iconography: Mapped[List["Iconography"]] = relationship(
        secondary=IconographyTheme.__table__,
        back_populates="theme"
    )


class Place(db.Model):
    __tablename__ = "place"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[Optional[str]]
    richelieu_url: Mapped[str] = mapped_column(unique=True)
    loc: Mapped[Dict] = mapped_column(JSON)
    plot: Mapped[Dict] = mapped_column(JSON)
    date_lower: Mapped[int]
    date_upper: Mapped[int]

    iconography: Mapped[List["Iconography"]] = relationship(
        secondary=IconographyPlace.__table__,
        back_populates="place"
    )


class Iconography(db.Model):
    __tablename__ = "iconography"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    iiif_manifest_url: Mapped[str]
    iiif_image_url: Mapped[str]
    source_url: Mapped[Optional[str]]
    richelieu_url: Mapped[str]
    date_lower: Mapped[Optional[int]]
    date_upper: Mapped[Optional[int]]
    institution: Mapped[str]
    id_author: Mapped[Optional[int]] = mapped_column(ForeignKey("author.id"))
    
    author: Mapped[Optional["Author"]] = relationship(back_populates="iconography")
    theme: Mapped[List["Theme"]] = relationship(
        secondary=IconographyTheme.__table__,
        back_populates="iconography"
    )
    place: Mapped[List["Place"]] = relationship(
        secondary=IconographyPlace.__table__,
        back_populates="iconography"
    )
    


