from flask import Flask

from app.utils.constants import DIR_TEMPLATES

app = Flask(
    "Jinja if",
    template_folder=DIR_TEMPLATES
)

from app.routes import generic