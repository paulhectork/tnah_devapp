from flask import render_template

from app.app import app

@app.route("/")
def index():
    app_name = "Catalogue Richelieu"
    return render_template("homepage.html", app_name=app_name)
