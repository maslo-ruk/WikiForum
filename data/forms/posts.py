from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class AddPostForm(FlaskForm):
    label = StringField('Название статьи')
    content = TextAreaField('Содержание')
    submit = SubmitField('Создать')
