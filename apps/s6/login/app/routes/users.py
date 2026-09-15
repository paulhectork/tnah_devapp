from flask import render_template, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required

from app.app import app, login_manager
from app.models.forms import UserCreateForm, UserLoginForm
from app.models.users import User
from app.utils.constants import APP_NAME


@app.route("/user/nouveau/", methods=["GET", "POST"])
def user_create():
    form = UserCreateForm()

    # form.validate_on_submit est True si:
    # - la requête est POST (on a soumis un formulaire)
    # - le formulaire est valide (wtforms a bien validé toutes les données fournies)
    if form.validate_on_submit():
        # on récupère les données et on les passe à create
        # `.data` permet de sélectionner la valeur fournie par l'utilisateur.ice
        user_name = form.user_name.data
        user_mail = form.user_mail.data
        user_password = form.user_password.data
        # `create` retourne:
        # - un booleen qui indique si la création réussi
        # - soit l'objet User crée, soit une liste d'erreurs
        success, data = User.create(
            user_name=user_name, 
            user_mail=user_mail, 
            user_password=user_password
        )
        # l'insert a réussi => rediriger sur la page d'accueil
        if success:
            flash("Compte utilisateur créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect("/")
        # l'insert a échoué => afficher les messages d'erreur.
        else: 
            data = "Les erreurs suivantes ont été repérées:" + ", ".join(data)
            flash(data, "error")
            return  render_template("pages/user_create.html", form=form, app_name=APP_NAME)
    return render_template("pages/user_create.html", form=form, app_name=APP_NAME)


@app.route("/user/connexion/", methods=["GET", "POST"])
def user_login():
    form = UserLoginForm()

    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.e", "success")
        return redirect("/")

    if form.validate_on_submit():
        user_mail = form.user_mail.data
        user_password = form.user_password.data
        user = User.get_user_by_credentials(
            user_mail=user_mail,
            user_password=user_password
        )
        if user:
            flash("Vous êtes maintenant connecté.e", "success")
            login_user(user)
            return redirect("/")
        else:
            flash("Identifiants incorrects", "error")
            return render_template("pages/user_login.html", form=form, app_name=APP_NAME)
        
    return render_template("pages/user_login.html", form=form, app_name=APP_NAME)


@app.route("/user/deconnexion/")
@login_required
def user_logout():
    logout_user()
    flash("Vous êtes déconnecté.e")
    return redirect("/")


login_manager.login_view = "user_login"
login_manager.login_message = "Veuillez vous conecter pour continuer"