from typing import Tuple, List

from flask_wtf import FlaskForm
from wtforms import StringField, URLField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Email

from app.models.data import Author, Theme, Place, Iconography
from app.app import app, db


def get_iconography_relationships() -> Tuple[List, List, List]:
    """
    retourne, pour chaque table avec laquelle Iconography 
    a une relation, une liste de (id, nom_de_objet) (chaque 
    item de la liste est une instance de la table).
    ces listes sont utilisées pour créer les champs des formulaires
    Iconography qui portent sur d'autres tables. 

    NOTE: en HTML, les valeurs sont représentées par des strings. 
    donc, on convertit tous nos ids en strings.
    """
    with app.app_context():
        # pour choisir l'auteur associé.e à une ressource 
        # iconographique, on crée une liste de `(id_auteur, nom_auteur)` 
        all_authors = db.session.execute(
            db.select(Author).order_by(Author.author_name)
        ).scalars().all()
        author_choices = [("", "Choisir un.e auteur.ice") ]
        for author in all_authors:
            author_choices.append(( str(author.id), author.author_name ))

        # pareil pour les thèmes
        all_themes = db.session.execute(
            db.select(Theme).order_by(Theme.theme_name)
        ).scalars().all()
        theme_choices = [ ("", "Choisir un thème") ]
        for theme in all_themes:
            theme_choices.append(( str(theme.id), theme.theme_name ))

        # pareil pour les lieux
        all_places = db.session.execute(
            db.select(Place).order_by(Place.address)
        ).scalars().all()
        place_choices = [ ("", "Choisir un lieu") ]
        for place in all_places:
            place_choices.append(( str(place.id), place.address ))
    return author_choices, theme_choices, place_choices


class IconographyCreateOrUpdateForm(FlaskForm):
    # on définit un champ par colonne de la table Iconography
    title = StringField(
        "Titre de la ressource", validators=[DataRequired()]
    )
    iiif_manifest_url = URLField(
        "URL du manifeste IIIF", validators=[DataRequired()]
    )
    iiif_image_url = URLField(
        "URL de l'image principale", validators=[DataRequired()]
    )
    source_url =  URLField(
        "URL de la source", validators=[Optional()]
    )
    richelieu_url = URLField(
        "URL sur le site Quartier Richelieu", validators=[DataRequired()]
    )
    date_lower = IntegerField(
        "Date", validators=[Optional()]
    )
    date_upper = IntegerField(
        "Date de fin (si nécessaire)", validators=[Optional()]
    )
    institution = StringField(
        "Institution", validators=[DataRequired()]
    )
    
    # on créée des champs pour les jointures
    id_author = SelectField(
        "Auteur", validators=[Optional()]
    )
    id_place = SelectField(
        "Lieu", validators=[Optional()]
    )
    id_theme = SelectField(
        "Thème", validators=[Optional()]
    )

    def __init__(self, icono_item: Iconography = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # NOTE: je bouge cette définition dans le __init__ car sinon il y a des erreurs d'import quand on lance des tests
        # on récupère les choix pour les tables de relations
        # à noter, les ID retournés par `get_iconography_relationships` sont représentés par des `str`.
        # il faudra les rétroconvertir à l'insert ou update
        author_choices, theme_choices, place_choices = get_iconography_relationships()
        self.id_author.choices = author_choices
        self.id_theme.choices = theme_choices
        self.id_place.choices = place_choices

        # on définit les défauts seulement si `icono_item` est défini
        if icono_item:
            
            # on récupère les ID de chaque relation à `icono_item`. ces ID seront 
            # utilisés comme défaut de `id_author`, `id_theme` et `id_place`
            id_author_default = None
            if icono_item.author:
                # on convertit nos ID par défaut en str pour coller avec ce qui est retourné par `get_iconography_relationships` 
                id_author_default = str(icono_item.author.id) 
            id_place_default = None 
            if len(icono_item.place):
                id_place_default = str(icono_item.place[0].id)
            id_theme_default = None 
            if len(icono_item.theme):
                id_theme_default = str(icono_item.theme[0].id)

            # on utilise `icono_item` pour définir toutes les valeurs par défaut du formulaire
            self.title.data = icono_item.title
            self.iiif_manifest_url.data = icono_item.iiif_manifest_url
            self.iiif_image_url.data = icono_item.iiif_image_url
            self.source_url.data = icono_item.source_url
            self.richelieu_url.data = icono_item.richelieu_url
            self.date_lower.data = icono_item.date_lower
            self.date_upper.data = icono_item.date_upper
            self.institution.data = icono_item.institution

            self.id_author.data = id_author_default
            self.id_place.data = id_place_default
            self.id_theme.data = id_theme_default


class UserCreateForm(FlaskForm):
    user_name = StringField("Nom d'utilisateur.ice", validators=[DataRequired(), Length(max=50)])
    user_mail = StringField("Email", validators=[DataRequired(), Email()])
    user_password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=50)])


class UserLoginForm(FlaskForm):
    user_mail = StringField("Email", validators=[DataRequired(), Email()])
    user_password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=50)])