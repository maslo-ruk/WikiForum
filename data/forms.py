from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SearchField
from wtforms.validators import DataRequired, InputRequired

class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = StringField('Ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddPostForm(FlaskForm):
    title = StringField('Название статьи')
    content = TextAreaField('Содержание', validators=[InputRequired()])
    tegs = TextAreaField('Теги', validators=[InputRequired()])
    submit = SubmitField('Создать')


class RegisterForm(FlaskForm):
    name = StringField('Ваш логин:', validators=[DataRequired()])
    email = StringField('Электронная почта:', validators=[DataRequired()])
    password = StringField('Ваш пароль:', validators=[DataRequired()])
    second_password = StringField('Повторите пароль:', validators=[DataRequired()])
    captchafield = StringField('Введите капчу:', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Создать')

class SearchPostForm(FlaskForm):
    title = SearchField('Название статьи')
    submit = SubmitField('Искать')


class EditForm(FlaskForm):
    name = StringField('Ваш логин', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class AddCommentForm(FlaskForm):
    content = TextAreaField('Оставить комментарий')
    submit = SubmitField('Готово')

class changeProfileForm(FlaskForm):
    name = StringField('Изменить логин:', validators=[DataRequired()])
    email = StringField('Изменить почту:', validators=[DataRequired()])
    password = StringField('Изменить пароль', validators=[DataRequired()])
    submit = SubmitField('Готово')

