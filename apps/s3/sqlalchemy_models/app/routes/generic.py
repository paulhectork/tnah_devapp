from flask import render_template
from sqlalchemy import text

from app.app import app, db
from app.utils.constants import APP_NAME
from 

@app.route("/")
def index():
    return render_template("pages/homepage.html", app_name=APP_NAME)

@app.route("/iconographie")
def icono_index():
    result = db.session.execute(text("SELECT * FROM iconography;"))
    icono_corpus = result.all()
    return render_template("pages/icono_index.html", app_name=APP_NAME, icono_corpus=icono_corpus)