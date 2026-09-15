from typing import Union, Tuple, List, Optional

from flask_login import UserMixin, login_user, logout_user
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str]
    user_mail: Mapped[str]
    user_password: Mapped[str]
    
    @staticmethod
    def create(user_mail: str, user_name: str, user_password: str) -> Tuple[bool, Union["User", str]]:
        """
        créer un nouveau user.

        notre fonction retourne:
        - (True, User) en cas de succès 
        - (False, <message d'erreur>) en cas d'erreur
        donc, le 1er item permet de savoir si l'insertion a fonctionné 
        """
        # on vérifie si il existe un autre `user` avec le même mail
        existing_user = db.session.execute(
            db.select(User).filter(User.user_mail == user_mail)
        ).scalars().all()
        # l'user existe => on n'insère pas et on retourne un message d'erreur
        if len(existing_user):
            return False, f"Un utilisateur existe déjà pour le mail: {user_mail}"

        # si l'user n'existe pas, on le crée. remarquez l'utilisation de `generate_password_hash`
        new_user = User(
            user_name=user_name,
            user_mail=user_mail,
            user_password=generate_password_hash(user_password)
        ) 

        # pour finir, on insère l'user
        try:
            db.session.add(new_user)
            db.session.commit()
            return True, new_user
        except Exception as e:
            # en cas d'erreur au moment de l'insert, on retourne False et le message d'erreur de l'appli
            print(e)
            return False, "Erreur à la création du compte utilisateur"

    @staticmethod
    def get_user_by_credentials(user_mail: str, user_password: str) -> Optional["User"]:
        """
        identifier un User par son mail et son mdp. 

        :returns: l'User si le mail et mdp sont valides, None sinon 
        """
        # retourne soit un `User`, soit None 
        user = db.session.execute(
            db.select(User).filter(User.user_mail == user_mail)
        ).scalars().first()
        # on vérifie que le `User` avec ce mail a bien le bon mot de passe
        if user and check_password_hash(user.user_password, user_password):
            return user
        # sinon, on retourne None
        return None


@login_manager.user_loader
def load_user(id_user: str):
    id_user = int(id_user)
    return db.session.get(User, id_user)


