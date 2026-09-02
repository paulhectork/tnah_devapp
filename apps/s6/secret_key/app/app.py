from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

# from sqlalchemy import text
# with app.app_context():
#     print(db.session.execute(text("select * from iconography")).all())

from app.routes import generic