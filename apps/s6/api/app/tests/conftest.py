import os

# pour éviter des problèmes de setup de l'appli, on définit FLASK_TESTING avant d'importer pytest
os.environ["FLASK_TESTING"] = "True"

import pytest

from app.app import app as flask_app, db as flask_db


@pytest.fixture(autouse=True)
def set_testing_env():
    yield
    # quand les tests sont finis, on supprime la vatriable d'env
    os.environ.pop("FLASK_TESTING", None)


@pytest.fixture()
def app():    
    # on désactive la validation CSRF pour pouvoir tester nos formulaires
    # (ATTENTION: ne jamais la désactiver sinon, ni en dev, ni en prod)
    flask_app.config['WTF_CSRF_ENABLED'] = False
    

    with flask_app.app_context():
        # db.create_all() est une commande SQLAlchemy qui permet de 
        # créer une base de données à partir des modèles qu'on a défini 
        # comme notre base de données de test est vide, on l'initialise
        flask_db.create_all()
        # yield est une forme particulière de `return`. 
        # ici, `yield` correspond à toute la durée d'exécution des tests.  
        yield flask_app
        # tout ce qui vient après le `yield` permet de nettoyer tout une fois que tous 
        # les tests se sont exécutés. ici, on supprime la base de données et son contenu.
        flask_db.session.remove()
        flask_db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    yield flask_db
        