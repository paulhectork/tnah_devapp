from flask import render_template
from sqlalchemy import text

from app.app import app, db
from app.utils.constants import APP_NAME
from app.models.data import Iconography, Author, Theme, Place

@app.route("/")
def index():
    """
    page d'accueil
    """
    # on affiche les 5 premiers résultats de Icono
    query = db.select(Iconography).order_by(Iconography.id.desc()).limit(10)
    icono_preview = db.session.execute( query ).scalars().all() 
    return render_template("pages/homepage.html", app_name=APP_NAME, icono_preview=icono_preview)


@app.route("/iconographie/")
def icono_index():
    """
    index des ressources icono
    """
    # on affiche tout l'index icono: 
    query = db.select(Iconography)
    icono_corpus = db.session.execute( query ).scalars().all() 
    return render_template("pages/icono_index.html", app_name=APP_NAME, icono_corpus=icono_corpus)


@app.route("/iconographie/<int:id_icono>")
def icono_main(id_icono: int):
    """
    vue principale d'une ressource icono
    """
    icono_item = db.get_or_404(Iconography, id_icono)
    return render_template("pages/icono_main.html", app_name=APP_NAME, icono_item=icono_item)


@app.route("/auteur/")
def author_index():
    """
    index des auteurices
    """
    author_list = db.session.execute( 
        db.select(Author).order_by(Author.author_name)
    ).scalars().all()
    return render_template("pages/author_index.html", app_name=APP_NAME, author_list=author_list)


@app.route("/auteur/<int:id_author>")
def author_main(id_author: int):
    """
    vue principale pour un.e Author
    """
    author_item = db.get_or_404(Author, id_author)
    return render_template("pages/author_main.html", app_name=APP_NAME, author_item=author_item)


@app.route("/theme/")
def theme_index():
    """
    index des thèmes
    """
    theme_list = db.session.execute( 
        db.select(Theme).order_by(Theme.theme_name)
     ).scalars().all()
    return render_template("pages/theme_index.html", app_name=APP_NAME, theme_list=theme_list)


@app.route("/theme/<int:id_theme>")
def theme_main(id_theme: int):
    """
    vue principale d'une ressource theme
    """
    theme_item = db.get_or_404(Theme, id_theme)
    return render_template("pages/theme_main.html", app_name=APP_NAME, theme_item=theme_item)


@app.route("/lieu/")
def place_index():
    """
    index des lieux
    """
    place_list = db.session.execute( 
        db.select(Place).order_by(Place.address)
    ).scalars().all()
    return render_template("pages/place_index.html", app_name=APP_NAME, place_list=place_list)


@app.route("/lieu/<int:id_place>")
def place_main(id_place: int):
    """
    vue principale d'une ressource place
    """
    place_item = db.get_or_404(Place, id_place)
    return render_template("pages/place_main.html", app_name=APP_NAME, place_item=place_item)
