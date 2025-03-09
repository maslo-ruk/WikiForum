from flask import Flask, url_for, request, render_template, redirect
from werkzeug.utils import secure_filename
import json
import os

from data.forms.AddPostForm import AddPostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FSFAFDSA'
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\egorzhsvor\\PycharmProjects\\WikiForum\\materials'
param = {'username': 'Егыч',
         'title': 'Егыч', 'number': 1}


@app.route('/index/<title>')
def index(title):
    param2 = param
    param2['title'] = title
    return render_template('index.html', **param)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        filename = secure_filename(form.content.data.filename)
        form.content.data.save('uploads/' + filename)
        return redirect('/index/ror')
    return render_template('add_post.html', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')