import pytest

from app.app import app as flask_app, db as flask_db


@pytest.fixture(autouse=True)
def set_testing_env():
    """
    définit FLASK_TESTING à True avant de lancer des tests, 
    ce qui permettra de sélectionner la bonne config dans `config_app` 
    """
    os.environ["FLASK_TESTING"] = "True"
    yield
    # quand les tests sont finis, on supprime la vatriable d'env
    os.environ.pop("FLASK_TESTING", None)


@pytest.fixture()
def app():
    app = flask_app
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite://:memory:",
        "TESTING": True
    })

    with app.app_context():
        # db.create_all() est une commande SQLAlchemy qui permet de 
        # créer une base de données à partir des modèles qu'on a défini 
        flask_db.create_all()
        # yield est une forme particulière de `return`. ici, `yield` correspond à 
        # toute la durée d'exécution des tests.  
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
    db = flask_db
    with app.app_context():
        yield db
        