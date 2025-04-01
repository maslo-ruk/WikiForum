from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    name = StringField('Ваш логин', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = StringField('Ваш пароль', validators=[DataRequired()])
    second_password = StringField('Ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Создать')
