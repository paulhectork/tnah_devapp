from flask import render_template

from app.app import app

icono = [
    {
        "id": 0,
        "auteurice": "Eugène Atget",
        "titre": "Palais Royal",
        "date": "1909-1927",
        "url": "https://quartier-richelieu.inha.fr/iconographie/qr12ad70f104f8245b69df7d1b35ac70b9f",
    },
    {
        "id": 1,
        "auteurice": "Jules Arnoult",
        "titre": "Palais Royal",
        "date": "1857-1870",
        "url": "https://quartier-richelieu.inha.fr/iconographie/qr12e06bf9e7d31433f9c3f266e8970404d",
    },
    {
        "id": 2,
        "auteurice": "Eugène Atget",
        "titre": "Hôtel de la Chancellerie d'Orléans : 19 rue des Bons Enfants",
        "date": "1905-1927",
        "url": "https://quartier-richelieu.inha.fr/iconographie/qr16ff0b86851cb4a36a340584318cb0f71",
    },
    {
        "id": 3,
        "auteurice": "Chiesi Zulimo pour Agence Rol",
        "titre": "Omnibus tiré par des chevaux, près du 9 rue de Valois, lieu de travail du photographe Zulimo Chiesi",
        "date": "1893-1900",
        "url": "https://quartier-richelieu.inha.fr/iconographie/qr1d4335d4decc24cdb971ba08874ab6126",
    },
    {
        "id": 4,
        "auteurice": "Agence Rol",
        "titre": "Groupe des délégués internationaux au 35e congrès de l'Union des sociétés de gymnastique de France",
        "date": "1908",
        "url": "https://quartier-richelieu.inha.fr/iconographie/qr10765fe0799654a79b8c2e3abb5107179",
    },
]

@app.route("/")
def index():
    app_name = "Catalogue Richelieu"
    return render_template("homepage.html", app_name=app_name, icono=icono)

@app.route("/iconographie/<int:id_icono>")
def icono_main(id_icono: int):
    for item in icono:
        if item["id"] == id_icono:
            item_icono = item
    return render_template("icono_main.html", item_icono=item_icono)
