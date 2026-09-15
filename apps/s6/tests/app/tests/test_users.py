from app.models.users import User


def test_create_user_ok(app, db, client):
    """
    test démontrant que la création d'utilisateur.ice.s fonctionne
    """
    response = client.post(
        '/user/nouveau/',
        data={
            'user_name': 'testuser',
            'user_mail': 'test@example.com',
            'user_password': 'securepassword123'
        }
    )

    # si la création d'utilisateurs a fonctionné, on est redirigé.e vers la page d'accueil.
    # le statut HTTP 302 fonctionne pour la redirection
    assert response.status_code == 302
    # on vérifie aussi qu'on est sur l'URL de la page d'accueil.
    assert response.location == '/'

    # ensuite, on vérifie que l'user a bien été crée
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(user_name='testuser')).scalars().first()
        assert user.user_mail == 'test@example.com'


def test_create_user_error(app, db, client):
    """
    test démontrant que la création d'utilisateur.ice.s avec les mauvaises données échoue
    """
    response = client.post(
        '/user/nouveau/',
        data={
            'user_name': None,
            'user_mail': 'test@example.com',
            'user_password': 'securepassword123'
        }
    )

    # la création ne devrait pas avoir fonctionné => il ne devrait pas y avoir de redirection
    assert response.status_code != 302

    # ensuite, on vérifie que aucun user n'a été crée
    with app.app_context():
        users = db.session.execute(db.select(User)).scalars().all()
        assert len(users) == 0
