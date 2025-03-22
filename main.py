from flask import Flask, url_for, request, render_template, redirect
from werkzeug.utils import secure_filename
import json
import os
from data import db_session
from data.users import User
from data.posts import Post

from data.forms.AddPostForm import AddPostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FSFAFDSA'
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\egorzhsvor\\PycharmProjects\\WikiForum\\materials'


@app.route('/index', methods=['GET', 'POST'])
def index():
    number = 1
    if request.method == 'GET':
        return render_template('index.html', number=number)
    elif request.method == 'POST':
        number += 1
    return render_template('index.html', number=number)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        name = form.name.data
        content = form.content.data
        create_post(name, content)
        return content
    return render_template('add_post.html', form=form)

def create_post(name, content):
    post = Post(name=name, content=content)
    db_sess = db_session.create_session()
    db_sess.add(post)
    db_sess.commit()

def main():
    db_session.global_init('db/wikiforum.db')
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()