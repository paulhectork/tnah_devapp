from typing import Optional, Union, List, Dict, Tuple

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

    @staticmethod 
    def create(
        title: str,
        iiif_manifest_url: str,
        iiif_image_url: str,
        source_url: Optional[str],
        richelieu_url: str,
        date_lower: Optional[int],
        date_upper: Optional[int],
        institution: str,
        id_author: Optional[int],
        id_place: Optional[int],
        id_theme: Optional[int],
    ) -> Tuple[bool, Union["Iconography",str]]:
        """
        créer un nouvel objet icono.
        :returns: (bool, icono|str).
            - bool indique le succès de l'insertion (si True, l'insertion a réussi)
            - si l'insertion a réussi, on retourne l'objet inséré, sinon on retourne un message d'erreur.
        """

        # 1. on crée un nouvel objet Iconography
        new_icono = Iconography(
            title=title,
            iiif_manifest_url=iiif_manifest_url,
            iiif_image_url=iiif_image_url,
            source_url=source_url,
            richelieu_url=richelieu_url,
            date_lower=date_lower,
            date_upper=date_upper,
            institution=institution
        )

        # 2. on ajoute les relations 
        if id_author:
            author = db.session.get(Author, id_author)
            new_icono.author = author
        if id_place:
            # pour new_icono.place et new_icono.theme, on ajoute les relations dans une liste:
            # il s'agit d'une liste de relations
            place = db.session.get(Place, id_place)
            new_icono.place.append(place)
        if id_theme:
            theme = db.session.get(Theme, id_theme)
            new_icono.theme.append(theme)

        # 2. on fait le commit
        # la base de donnée est un système "externe" avec son propre système de validation.
        # un problème est toujours théoriquement possible, donc on met un try...execpt
        try:
            db.session.add(new_icono)
            db.session.commit()

            return True, new_icono
        except Exception as e:
            db.session.rollback()
            print(e)
            return False, "Erreur à l'insertion dans la base de données."

    def update(
        self,
        title: str,
        iiif_manifest_url: str,
        iiif_image_url: str,
        source_url: Optional[str],
        richelieu_url: str,
        date_lower: Optional[int],
        date_upper: Optional[int],
        institution: str,
        id_author: Optional[int],
        id_place: Optional[int],
        id_theme: Optional[int],
    ) -> Tuple[bool, Union["Iconography",str]]:
        """
        modifier un objet icono existant en base.
        :returns: (bool, icono|str).
            - bool indique le succès de l'update (si True, l'update a réussi)
            - si l'update a réussi, on retourne l'objet mis à jour, sinon on retourne un message d'erreur.
        """        
        # 1. on met à jour tous les champs
        self.title = title
        self.iiif_manifest_url = iiif_manifest_url
        self.iiif_image_url = iiif_image_url
        self.source_url = source_url
        self.richelieu_url = richelieu_url
        self.date_lower = date_lower
        self.date_upper = date_upper
        self.institution = institution

        # 2. on ajoute les relations 
        # on remplace les anciennes relations par des nouvelles, donc on 
        # n'utilise pas append ici, contrairement à sans `Iconography.create()`
        if id_author:
            author = db.session.get(Author, id_author)
            self.author = author
        else:
            self.author = None
        if id_place:
            place = db.session.get(Place, id_place)
            self.place = [place]
        else:
            self.place = []
        if id_theme:
            theme = db.session.get(Theme, id_theme)
            self.theme = [theme]
        else:
            self.theme = []

        # 3. on sauvegarde les changements
        try:
            db.session.add(self)
            db.session.commit()
            return True, self
        except Exception as e:
            db.session.rollback()
            print(e)
            return False, "Erreur dans la mise à jour"

    def delete(self) -> bool:
        """
        supprimer une ressource iconographique. comme toujours, `self` est une instance de `Iconography` représente la ressource icono 

        :returns: 
            - True si la suppression réussit
            - False sinon
        """
        try:
            # on supprime les relations
            self.theme.clear()
            self.place.clear()

            # on supprime l'objet lui-même
            db.session.delete(self)
            db.session.commit()
            return True

        except Exception as e:
            print(e)
            return False
