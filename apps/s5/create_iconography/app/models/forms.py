from typing import Tuple, List

from flask_wtf import FlaskForm
from wtforms import StringField, URLField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from app.models.data import Author, Theme, Place
from app.app import app, db


def get_iconography_relationships() -> Tuple[List, List, List]:
    """
    retourne, pour chaque table avec laquelle Iconography 
    a une relation, une liste de (id, nom_de_objet) (chaque 
    item de la liste est une instance de la table).
    ces listes sont utilisées pour créer les champs des formulaires
    Iconography qui portent sur d'autres tables. 
    """
    with app.app_context():
        # pour choisir l'auteur associé.e à une ressource 
        # iconographique, on crée une liste de `(id_auteur, nom_auteur)` 
        all_authors = db.session.execute(
            db.select(Author).order_by(Author.author_name)
        ).scalars().all()
        author_choices = []
        for author in all_authors:
            author_choices.append(( author.id, author.author_name ))

        # pareil pour les thèmes
        all_themes = db.session.execute(
            db.select(Theme).order_by(Theme.theme_name)
        ).scalars().all()
        theme_choices = []
        for theme in all_themes:
            theme_choices.append(( theme.id, theme.theme_name ))

        # pareil pour les lieux
        all_places = db.session.execute(
            db.select(Place).order_by(Place.address)
        ).scalars().all()
        place_choices = []
        for place in all_places:
            place_choices.append(( place.id, place.address ))
    return author_choices, theme_choices, place_choices


class IconographyCreateForm(FlaskForm):
    # on récupère les choix pour les tables de relations
    author_choices, theme_choices, place_choices = get_iconography_relationships()

    # on définit un champ par colonne de la table Iconography
    title = StringField("Titre de la ressource", validators=[DataRequired(), Length(max=50)])
    iiif_manifest_url = URLField("URL du manifeste IIIF", validators=[DataRequired()])
    iiif_image_url = URLField("URL de l'image principale", validators=[DataRequired()])
    source_url =  URLField("URL de la source", validators=[Optional()])
    richelieu_url = URLField("URL sur le site Quartier Richelieu", validators=[DataRequired()])
    date_lower = IntegerField("Date", validators=[Optional()])
    date_upper = IntegerField("Date de fin (si nécessaire)", validators=[Optional()])
    institution = StringField("Institution", validators=[DataRequired()])
    
    # on créée des champs pour les jointures
    id_author = SelectField("Auteur", choices=author_choices, validators=[DataRequired()])
    id_place = SelectField("Lieu", choices=place_choices, validators=[DataRequired()])
    id_theme = SelectField("Thème", choices=theme_choices, validators=[DataRequired()])
