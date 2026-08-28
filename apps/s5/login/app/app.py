from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.utils.constants import DIR_TEMPLATES, DIR_STATICS, PATH_DB, APP_NAME, SECRET_KEY

print(">>>", PATH_DB)

app = Flask(
    APP_NAME,
    template_folder=DIR_TEMPLATES, 
    static_folder=DIR_STATICS
)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{PATH_DB}"
app.config["SECRET_KEY"] = SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app.routes import generic, users