from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class UserCreateForm(FlaskForm):
    user_name = StringField("Nom d'utilisateur.ice", validators=[DataRequired(), Length(max=50)])
    user_mail = StringField("Email", validators=[DataRequired(), Email()])
    user_password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=50)])


class UserLoginForm(FlaskForm):
    user_mail = StringField("Email", validators=[DataRequired(), Email()])
    user_password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=50)])