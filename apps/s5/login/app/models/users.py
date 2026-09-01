from typing import Union, Tuple, List, Optional

from flask_login import UserMixin, login_user, logout_user
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.app import db, login_manager


class IconographyUser(db.Model):
    __tablename__ = "iconography_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_iconography: Mapped[int] = mapped_column(ForeignKey("iconography.id"))
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"))


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str]
    user_mail: Mapped[str]
    user_password: Mapped[str]
    
    iconography: Mapped[List["Iconography"]] = relationship(
        back_populates="user",
        secondary=IconographyUser.__table__
    )  

    @staticmethod
    def create_user(user_mail: str, user_name: str, user_password: str) -> Tuple[bool, Union["User", List[str]]]:
        """
        créer un nouveau user.

        notre fonction retourne:
        - False, <message d'erreur> en cas d'erreur
        - True, User en cas de succès 
        donc, le 1er item permet de savoir si l'insertion a fonctionné 
        """
        # liste de nos erreurs
        errors = []

        # 1. on vérifie que l'utilisateur.ice a fourni toutes les données
        if user_mail is None:
            errors.append("Veuillez fournir un email")
        if user_name is None:
            errors.append("Veuillez fournir un nom d'utilisateur")
        if user_password is None:
            errors.append("Veuillez fournir un mot de passe")

        # on vérifie si il existe un autre `user` avec le même mail
        existing_user = db.session.execute(
            db.select(User).filter(User.user_mail == user_mail)
        ).scalars().all()
        if len(existing_user):
            errors.append(f"Un utilisateur existe déjà pour le mail: {user_mail}")

        # il y a eu des erreurs => pas d'insert
        if len(errors):
            return False, errors

        # pas d'erreurs => on fait l'insert
        new_user = User(
            user_name=user_name,
            user_mail=user_mail,
            user_password=generate_password_hash(user_password)
        ) 
        try:
            db.session.add(new_user)
            db.session.commit()
            return True, new_user
        except Exception as e:
            # en cas d'erreur au moment de l'insert, on retourne False et le message d'erreur de l'appli
            # on retourne le message d'erreur dans une liste
            print(e)
            return False, [str(e)]

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


