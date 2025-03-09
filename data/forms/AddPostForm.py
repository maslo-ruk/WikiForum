from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class AddPostForm(FlaskForm):
    name = StringField('Ваш логин', validators=[DataRequired()])
    label = StringField('Название статьи')
    content = FileField("Содержание")
    submit = SubmitField('Создать')
