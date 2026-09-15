# tests basiques vérifiant que notre configuration est correcte

# tester la config de l'appli
def test_config(app):
    assert app.config["TESTING"] is True
    assert "memory" in str(app.config["SQLALCHEMY_DATABASE_URI"])

# tester que le client fonctionne bien (on peut faire des requêtes sur nitre appli)
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

# ce test va planter
def test_home_page(client):
    response = client.get('/route/qui/nexiste/pas')
    # on va se manger un status code 404 => l'assert ci-dessous rate => nos tests ne réussissent pas
    assert response.status_code == 200

