import shutil

from flask import Flask, request, render_template, redirect, jsonify
from data.functions import *
from data.posts_api import PostResourse, PostListResource
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.forms import *
from flask_restful import reqparse, abort, Api, Resource
from data.comment import Comment


from werkzeug.utils import secure_filename
import json
import os
from data import db_session
from data.users import User
from data.posts import Post
from data.config import *

app = Flask(__name__)
news_api = Api(app)
app.config['SECRET_KEY'] = 'FSFAFDSA'
UPLOAD_FOLDER = 'static/image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/wikiforum.db")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/testtt', methods =['POST'])
def testtt():
    print(request.json)


@app.route('/', methods=['GET', 'POST'])
def index():
    s_form = SearchPostForm()
    session = db_session.create_session()
    posts = session.query(Post).order_by(Post.views)[::-1]
    if request.method == 'POST':
        if s_form.validate_on_submit():
            text = s_form.title.data
            return redirect(f'/search/{text}')
        print(request.json)
    session.close()
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
    session.close()
    return render_template('search_post.html', search_form=s_form, posts=right_posts)


@app.route("/edit_profile", methods=["get", "post"])
def edit_profile():
    form = EditForm()
    session = db_session.create_session()
    cu = session.query(User).filter(User.id == current_user.id).first()
    if form.validate_on_submit():
        cu.name = form.name.data
        cu.email = form.email.data
        session.commit()
        session.close()
        return redirect(f'/profile')
    session.commit()
    session.close()
    return render_template('edit.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    session = db_session.create_session()
    if request.method == 'POST':
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
            try:
                file = request.files['files']
                if file and allowed_file(file.filename):
                    photo = f'{user.id}.{file.filename.rsplit(".", 1)[1]}'
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/profile_pictures', photo))
                    user.photo_path = f'static/image/profile_pictures/{photo}'
                else:
                    photo = STANDART_PHOTO
            except Exception:
                photo = STANDART_PHOTO
            login_user(user, remember=form.remember_me.data)
            session.commit()
            session.close()
            return redirect('/')
    session.close()
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
        session.commit()
        session.close()
        return redirect('/')
    session.commit()
    session.close()
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/add_post', methods=['GET', 'POST'])
def add_postt():
    if current_user.is_authenticated:
        session = db_session.create_session()
        all_tags_ = session.query(Tag).all()
        all_tags = []
        for i in all_tags_:
            all_tags.append(i.to_dict())
        print(all_tags)
        if request.method == 'POST':
            name = request.form['title']
            story = request.form["story"]
            tags = request.form.getlist("tags")
            files = request.files.getlist("files")
            idd = current_user.id
            add_post(name, story, list(map(int, tags)), idd)
            session = db_session.create_session()
            post = session.query(Post).all()[-1]
            post_id = post.id
            count = 0
            for file in files:
                count += 1
                try:
                    if file and allowed_file(file.filename):
                        photo = f'{post_id}_{count}.{file.filename.rsplit(".", 1)[1]}'
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/post_pictures', photo))
                        post.photos_paths += f'{os.path.join(app.config["UPLOAD_FOLDER"])}/post_pictures/{post_id}_{count}.{file.filename.rsplit(".", 1)[1]} '
                    else:
                        photo = STANDART_PHOTO
                except Exception:
                    pass
            session.commit()
            session.close()
        session.commit()
        session.close()
        return render_template('add_post-2.html', tags=all_tags)
    else:
        return redirect('/not_authenticated')


@app.route('/not_authenticated')
def not_authenticated():
    return render_template('not_authenticated.html')


@app.route('/post/<id>', methods=['GET', 'POST'])
def postt(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id).first()
    button_text = 'Нравится'
    photo_paths = post.photos_paths.split(' ')
    photo_paths.remove('')
    comment_form = AddCommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            content = comment_form.content.data
            comment = Comment()
            if not comment:
                return False
            comment.content = content
            comment.user = session.query(User).filter(User.id == current_user.id).first()
            comment.post = post
            session.add(comment)
            comment_form.content.data = ""

        else:
            comment_form.content.data = "Пожалуйста, зарегистрируйся!"
    if current_user.is_authenticated:
        cu = session.query(User).filter(User.id == current_user.id).first()
        read = cu.read_posts
        if post not in read:
            post.views += 1
            cu.read_posts.append(post)
        if post not in cu.liked_posts:
            button_text = 'Нравится'
        else:
            button_text = 'Убрать из понравившегося'
    post_ = post.to_dict()

    session.commit()
    session.close()
    post_test = session.query(Post).filter(Post.id == id).first()
    print(post_test.comments)
    return render_template('post.html', post=post_, p_id=post_['id'], button_text=button_text,
                           paths=photo_paths, tags=session.query(Tag).all(), comment_form=comment_form, post_test=post_test)

@app.route('/like/<id>')
def like(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        post = session.query(Post).filter(Post.id == id).first()
        user = session.query(User).filter(User.id == current_user.id).first()
        if post not in user.liked_posts:
            user.liked_posts.append(post)
            post.likes += 1
        else:
            user.liked_posts.remove(post)
            post.likes -= 1
        session.commit()
    return redirect(f'/post/{id}')

@app.route('/profile')
def account():
    user_id = current_user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    nick_name = user.name
    photo = user.photo_path
    email = user.email
    db_sess.close()
    return render_template('profile.html', title='Ваш профиль', name=nick_name, email=email,
                           photo=photo)

@app.route('/tag/<id>')
def tag(id):
    session = db_session.create_session()
    posts = find_posts_by_tag(id)
    session.close()
    return render_template('tag_page.html', posts=posts)


def main():
    db_session.global_init('db/wikiforum.db')
    news_api.add_resource(PostResourse, '/posts/<int:post_id>')
    news_api.add_resource(PostListResource, '/posts')
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()