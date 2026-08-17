from flask import render_template

from app.app import app

app_name = "Catalogue Richelieu"

# on ajoute quelques ressources iconographiques à notre site et on passe `icono` à `render_template`:
icono = [
    "Palais Royal (1909-1927)",
    "Palais Royal (1857-1870)",
    "Hôtel de la Chancellerie d'Orléans : 19 rue des Bons Enfants",
    "Omnibus tiré par des chevaux, près du 9 rue de Valois, lieu de travail du photographe Zulimo Chiesi",
    "Groupe des délégués internationaux au 35e congrès de l'Union des sociétés de gymnastique de France",
]

# puis on passe `icono` à `render_template`. `icono` devient maintenant une variable utilisable côté Jinja
@app.route("/")
def index():
    return render_template("homepage.html", app_name=app_name, icono=icono)