from flask import render_template, url_for, redirect, flash, request, jsonify

from app.app import app, db
from app.models.data import Iconography, Author, Theme, Place
from app.models.forms import IconographyCreateOrUpdateForm


@app.route("/api/iconographie")
def api_icono_index():
    # on récupère tout notre corpus iconographique
    icono_corpus = db.session.execute(
        db.select(Iconography)
    ).scalars()

    # notre variable de sortie
    icono_list = []
    for icono_item in icono_corpus:
        # icono_dict est une représentation de `icono_item` sous forme de dictionnaire
        icono_dict = {
            "id": icono_item.id,
            "title": icono_item.title,
            "date_lower": icono_item.date_lower,
            "date_upper": icono_item.date_upper or None,
            "institution": icono_item.institution,
        }

        # on le complète avec les relations
        if icono_item.author:
            icono_dict["author"] = icono_item.author.author_name
        if icono_item.place:
            places = []
            for place in icono_item.place:
                places.append(place.address)
        icono_dict["places"] = places
        if icono_item.theme:
            themes = []
            for theme in icono_item.theme:
                themes.append(theme.theme_name)
        icono_dict["themes"] = themes

        # on l'ajoute à icono_list
        icono_list.append(icono_dict)
    
    return jsonify(icono_list)


@app.route("/api/iconographie/<int:id_icono>")
def api_icono_main(id_icono: int):
    # on récupère tout notre corpus iconographique
    icono_item = db.get_or_404(Iconography, id_icono)

    # notre variable de sortie
    icono_dict = {
        "id": icono_item.id,
        "title": icono_item.title,
        "date_lower": icono_item.date_lower,
        "date_upper": icono_item.date_upper or None,
        "institution": icono_item.institution,
    }

    # on complète le dict avec les relations
    if icono_item.author:
        icono_dict["author"] = icono_item.author.author_name
    if icono_item.place:
        places = []
        for place in icono_item.place:
            places.append(place.address)
    icono_dict["places"] = places
    if icono_item.theme:
        themes = []
        for theme in icono_item.theme:
            themes.append(theme.theme_name)
    icono_dict["themes"] = themes

    # on retourne le dict    
    return jsonify(icono_dict)
