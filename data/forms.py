from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SearchField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = StringField('Ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddPostForm(FlaskForm):
    label = StringField('Название статьи')
    content = TextAreaField('Содержание')
    submit = SubmitField('Создать')


class RegisterForm(FlaskForm):
    name = StringField('Ваш логин', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = StringField('Ваш пароль', validators=[DataRequired()])
    second_password = StringField('Ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Создать')

class SearchPostForm(FlaskForm):
    title = SearchField('Название статьи')
    submit = SubmitField('Искать')


class AddCommentForm(FlaskForm):
    content = TextAreaField('Оставить комментарий')
    submit = SubmitField('Готово')