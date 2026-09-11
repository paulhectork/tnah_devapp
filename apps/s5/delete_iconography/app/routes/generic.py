from flask import render_template, url_for, redirect, flash, request
from sqlalchemy import text

from app.app import app, db
from app.utils.constants import APP_NAME
from app.models.data import Iconography, Author, Theme, Place
from app.models.forms import IconographyCreateOrUpdateForm# IconographyCreateForm, IconographyUpdateForm


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


@app.route("/iconographie/nouveau", methods=["GET", "POST"])
def icono_create():
    """
    vue pour créer une nouvelle ressource iconographique
    """
    form = IconographyCreateOrUpdateForm()

    if form.validate_on_submit():
        title = form.title.data
        iiif_manifest_url = form.iiif_manifest_url.data
        iiif_image_url = form.iiif_image_url.data
        source_url = form.source_url.data
        richelieu_url = form.richelieu_url.data
        date_lower = form.date_lower.data
        date_upper = form.date_upper.data
        institution = form.institution.data

        # on rétroconvertit en int les IDs qui sont représentés par des strings côté formulaire.
        id_author = None
        if form.id_author.data:
            id_author = int(form.id_author.data)
        id_theme = None
        if form.id_theme.data:
            id_theme = int(form.id_theme.data)
        id_place = None
        if form.id_place.data:
            id_place = int(form.id_place.data)

        success, data = Iconography.create(
            title=title,
            iiif_manifest_url=iiif_manifest_url,
            iiif_image_url=iiif_image_url,
            source_url=source_url,
            richelieu_url=richelieu_url,
            date_lower=date_lower,
            date_upper=date_upper,
            institution=institution,
            id_author=id_author,
            id_place=id_place,
            id_theme=id_theme
        )
        if success: 
            flash(f"Nouvelle ressource iconographique créée avec succès: {data.id}", "success")
            return redirect(url_for("icono_main", id_icono=data.id))
        else:
            flash(f"Erreur à la création d'une ressource iconographique: {data}", "error")
            return render_template("pages/icono_create.html", app_name=APP_NAME, form=form)
    
    return render_template("pages/icono_create.html", app_name=APP_NAME, form=form)


@app.route("/iconographie/<int:id_icono>/modifier", methods=["GET", "POST"])
def icono_update(id_icono: int):
    """
    vue pour modifier une ressource iconographique existante
    """
    # todo Iconography.update() method 

    icono_item = db.get_or_404(Iconography, id_icono)
 
    form = IconographyCreateOrUpdateForm(icono_item=icono_item)
 
    if form.validate_on_submit():
        title = form.title.data
        iiif_manifest_url = form.iiif_manifest_url.data
        iiif_image_url = form.iiif_image_url.data
        source_url = form.source_url.data
        richelieu_url = form.richelieu_url.data
        date_lower = form.date_lower.data
        date_upper = form.date_upper.data
        institution = form.institution.data

        # on rétroconvertit en int les IDs qui sont représentés par des strings côté formulaire.
        id_author = None
        if form.id_author.data:
            id_author = int(form.id_author.data)
        id_theme = None
        if form.id_theme.data:
            id_theme = int(form.id_theme.data)
        id_place = None
        if form.id_place.data:
            id_place = int(form.id_place.data)
            
        success, data = icono_item.update(
            title=title,
            iiif_manifest_url=iiif_manifest_url,
            iiif_image_url=iiif_image_url,
            source_url=source_url,
            richelieu_url=richelieu_url,
            date_lower=date_lower,
            date_upper=date_upper,
            institution=institution,
            id_author=id_author,
            id_place=id_place,
            id_theme=id_theme
        )
        if success: 
            flash(f"Ressource iconographique mise à jour avec succès: {data.id}", "success")
            return redirect(url_for("icono_main", id_icono=data.id))
        else:
            flash(f"Erreur à la mise à jour d'une ressource iconographique: {data}", "error")
            return render_template("pages/icono_update.html", app_name=APP_NAME, form=form, icono_item=icono_item)
    
    return render_template("pages/icono_update.html", app_name=APP_NAME, form=form, icono_item=icono_item)


@app.route("/iconography/<int:id_icono>/supprimer", methods=["GET", "POST"])
def icono_delete(id_icono: int):
    """
    supprimer une ressource iconographique
    """
    icono_item = db.get_or_404(Iconography, id_icono)

    if request.method == "POST":
        success = icono_item.delete()
        if success:
            flash("Ressource iconographique supprimée avec succès", "success")
            return redirect(url_for("icono_index"))    
        else:
            flash("Erreur à la suppression de la ressource iconographique", "error")
            return render_template("pages/icono_delete.html", app_name=APP_NAME, icono_item=icono_item)
    
    return render_template("pages/icono_delete.html", app_name=APP_NAME, icono_item=icono_item)


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

