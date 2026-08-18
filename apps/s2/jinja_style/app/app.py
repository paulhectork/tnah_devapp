from flask import Flask

from app.utils.constants import DIR_TEMPLATES, DIR_STATICS

app = Flask(
    "Catalogue Richelieu",
    template_folder=DIR_TEMPLATES, 
    static_folder=DIR_STATICS
)

from app.routes import generic