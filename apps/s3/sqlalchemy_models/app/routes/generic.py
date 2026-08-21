from flask import render_template
from sqlalchemy import text

from app.app import app, db
from app.utils.constants import APP_NAME
from app.models.data import Iconography

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