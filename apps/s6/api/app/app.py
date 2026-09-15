import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.utils.constants import DIR_TEMPLATES, DIR_STATICS, PATH_DB, APP_NAME, SECRET_KEY

def config_app(app):
    """
    configurations de l'app en fonction du contexte d'exécution. 

    on définit deux contextes grâce à la variable d'environnement 
    `FLASK_TESTING`. elle est définie dans `app/tests/conftest.py`

    - FLASK_TESTING=True -> tests
    - FLASK_TESTING=False -> fonctionnement normal
    
    NOTE: cette config est simple, mais en temps normal on a besoin 
    de 3 configs au moins: développement, tests et production.
    il vaut mieux définir des classes, où chaque classe correspond à une 
    config différente. suivez ce guide: 
    https://flask.palletsprojects.com/en/stable/config/#configuration-best-practices
    """
    
    # on cherche la variable d'env `FLASK_TESTING` avec `os.getenv`
    # si elle n'est pas définie, notre valeur par défault est "False"
    # `FLASK_TESTING` est définie dans `app/tests/conftest.py`
    testing = os.getenv("FLASK_TESTING", "False").lower() == "true"

    if testing:
        app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
    else:
        app.config.update({
            "TESTING": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{PATH_DB}"
        })

    return app


app = Flask(
    APP_NAME,
    template_folder=DIR_TEMPLATES, 
    static_folder=DIR_STATICS
)
app.config["SECRET_KEY"] = SECRET_KEY
app = config_app(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


from app.routes import generic, users, api