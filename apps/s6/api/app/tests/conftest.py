import os

# pour éviter des problèmes de setup de l'appli, on définit FLASK_TESTING avant d'importer pytest
os.environ["FLASK_TESTING"] = "True"

import pytest

from app.app import app as flask_app, db as flask_db
from app.models.data import Iconography


@pytest.fixture(autouse=True)
def set_testing_env():
    yield
    # quand les tests sont finis, on supprime la vatriable d'env
    os.environ.pop("FLASK_TESTING", None)

@pytest.fixture(autouse=True)
def set_base_icono(app, db):
    icono_item = Iconography(
        date_lower = 1910,
        institution = "Biblioth\u00e8que nationale de France",
        title = "[Lucie d'Avray. Palais Royal]",
        iiif_image_url = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b530124015/f1/full/1000/0/native.jpg",
        iiif_manifest_url = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b530124015/manifest.json",
        richelieu_url = "https://quartier-richelieu.inha.fr/iconographie/qr1703e89942a0c4fd08052e91956f67719",
        source_url = "https://gallica.bnf.fr/ark:/12148/btv1b530124015",
    )
    with app.app_context():
        db.session.add(icono_item)
        db.session.commit()
        item_id = icono_item.id
        yield


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
        