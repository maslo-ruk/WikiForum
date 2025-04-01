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

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        name = form.label.data
        content = form.content.data
        add_post(name, content, 1)
        return content
    return render_template('add_post.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    from data.forms.RegisterForm import RegisterForm
    form = RegisterForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password1, password2 = form.password.data, form.second_password.data
        if session.query(User).filter(User.email == email).first():
            return render_template('register.html', form=form, message='Такой пользователь уже есть!')
        if password1 != password2:
            return render_template('register.html', form=form, message='Пароли не совпадают!')
        user = User()
        user.fill_data(name, email)
        user.set_password(password1)
        session.add(user)
        session.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        name = form.label.data
        content = form.content.data
        add_post(name, content, 1)
        return content
    return render_template('add_post.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from data.forms.loginform import LoginForm
    form = LoginForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if not session.query(User).filter(User.email == email).first():
            return render_template('register.html', form=form, message='Нет такого пользователя')
        user = session.query(User).filter(User.email == email).first()
        if not user.check_password(password):
            return render_template('register.html', form=form, message='Неверный пароль')
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('login.html', form=form)

@app.route('/post/<id>')
def post(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id).first()
    return render_template('post.html', post=post)


@app.route('/tag/<id>')
def tag(id):
    session = db_session.create_session()
    posts = find_posts_by_tag(id)
    return render_template('tag_page.html', posts=posts)

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