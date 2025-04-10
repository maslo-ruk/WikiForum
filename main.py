from flask import Flask, request, render_template, redirect, jsonify
from data.functions import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.forms import *

from werkzeug.utils import secure_filename
import json
import os
from data import db_session
from data.users import User
from data.posts import Post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FSFAFDSA'
app.config['UPLOAD_FOLDER'] = 'materials'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/wikiforum.db")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/', methods=['GET', 'POST'])
def index():
    s_form = SearchPostForm()
    session = db_session.create_session()
    posts = session.query(Post).order_by(Post.views)[::-1]
    if s_form.validate_on_submit():
        text = s_form.title.data
        return redirect(f'/search/{text}')
    return render_template('index.html', search_form=s_form, posts = posts, tags=session.query(Tag).all())

@app.route('/search/<text>',  methods=['GET', 'POST'])
def search(text):
    s_form = SearchPostForm()
    if s_form.validate_on_submit():
        ttext = s_form.title.data
        return redirect(f'/search/{ttext}')
    session= db_session.create_session()
    posts = session.query(Post).order_by(Post.views)[::-1]
    right_posts = []
    for i in posts:
        if text in i.title or text in i.content:
            right_posts.append(i)
    return render_template('search_post.html', search_form=s_form, posts=right_posts)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post_web():
    form = AddPostForm()
    if form.validate_on_submit():
        name = form.label.data
        content = form.content.data
        add_post(name, content, 1)
        return content
    return render_template('add_post.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        add_user(name, email, password1)
        session = db_session.create_session()
        user = session.query(User).all()[-1]
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if not session.query(User).filter(User.email == email).first():
            return render_template('login.html', form=form, message='Нет такого пользователя')
        user = session.query(User).filter(User.email == email).first()
        if not user.check_password(password):
            return render_template('login.html', form=form, message='Неверный пароль')
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        name = form.label.data
        content = form.content.data
        add_post(name, content, 1)
        return content
    return render_template('add_post.html', form=form)


@app.route('/post/<id>')
def post(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id).first()
    if current_user.is_authenticated:
        cu = session.query(User).filter(User.id == current_user.id).first()
        read = cu.read_posts
        if post not in read:
            post.views += 1
            cu.read_posts.append(post)
    session.commit()
    return render_template('post.html', post=post)

@app.route('/profile')
def profile():
    user_id = current_user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    nick_name = user
    email = "почта@ладлыф"
    return render_template('profile.html', title='Ваш профиль', name=nick_name, email=email)

@app.route('/tag/<id>')
def tag(id):
    session = db_session.create_session()
    posts = find_posts_by_tag(id)
    return render_template('tag_page.html', posts=posts)


def main():
    db_session.global_init('db/wikiforum.db')
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()