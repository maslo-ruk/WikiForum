from flask import Flask, url_for, request, render_template, redirect
from werkzeug.utils import secure_filename
import json
import os
from data import db_session
from data.users import User
from data.posts import Post
from data.functions import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.forms.posts import AddPostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FSFAFDSA'
app.config['UPLOAD_FOLDER'] = 'materials'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/', methods=['GET', 'POST'])
def index():
    number = 1
    session = db_session.create_session()
    if request.method == 'GET':
        return render_template('index.html', number=number, posts = session.query(Post).all(), tags=session.query(Tag).all())
    elif request.method == 'POST':
        number += 1
    return render_template('index.html', number=number, posts = session.query(Post).all(), tags=session.query(Tag).all())


@app.route('/post/<id>')
def post(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id).first()
    return render_template('post.html', post=post)


# @app.route('/')
# def main_page():
#     if current_user.is_authenticated:
#         print('d')
#     else:
#         print('f')


def main():
    db_session.global_init('db/wikiforum.db')
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()