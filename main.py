import shutil

from flask import Flask, request, render_template, redirect, jsonify, make_response
from data.functions import *
from data.posts_api import PostResourse, PostListResource
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.forms import *
from flask_restful import reqparse, abort, Api, Resource


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


@app.route('/testt', methods =['GET','POST'])
def testtt():
    if request.method == 'POST':
        sort_by = request.cookies.get("sort_by", 0)
        print(request.data)
        if sort_by:
            print('abaaba')
            res = make_response(
                {'success': True})
            res.set_cookie("sort_by", request.json['sort_by'],
                           max_age=60 * 60 * 24 * 365 * 2)
        else:
            res = make_response(
                {'success': True})
            res.set_cookie("sort_by", request.json['sort_by'],
                           max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/', methods=['GET', 'POST'])
def index():
    s_form = SearchPostForm()
    session = db_session.create_session()
    posts = session.query(Post).order_by(Post.views)[::-1]
    x = request.cookies.get('sort_by')
    if request.method == 'POST':
        if s_form.validate_on_submit():
            text = s_form.title.data
            return redirect(f'/search/{text}')
    session.close()
    if not x:
        res = make_response(render_template('index.html', search_form=s_form, posts=posts,
                                            tags=session.query(Tag).all(), x='popularity'))
        res.set_cookie("sort_by", 'popularity',
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(render_template('index.html', search_form=s_form, posts=posts,
                                            tags=session.query(Tag).all(), x=request.cookies.get('sort_by')))
    return res

@app.route('/search/<text>', methods=['GET', 'POST'])
def search(text):
    s_form = SearchPostForm()
    if s_form.validate_on_submit():
        ttext = s_form.title.data
        return redirect(f'/search/{ttext}')
    session = db_session.create_session()
    posts = session.query(Post).order_by(Post.views)[::-1]
    right_posts = []
    other_posts = []
    for i in posts:
        print(text)
        print(i.keywords.split(' '))
        print(text in i.keywords.split(' '))
        if text in i.title or text in i.keywords.split(' '):
            right_posts.append(i)
        elif text in i.content:
            other_posts.append(i)
    session.close()
    return render_template('search_post.html', search_form=s_form, posts=right_posts)


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
        if request.method == 'POST':
            name = request.form['title']
            story = request.form["story"]
            keywords = request.form["keywords"]
            tags = request.form.getlist("tags")
            files = request.files.getlist("files")
            idd = current_user.id
            add_post(name, story, list(map(int, tags)), idd)
            session = db_session.create_session()
            post = session.query(Post).all()[-1]
            post.keywords = keywords
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
            return redirect(f'/post/{post_id}')
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
    author = post.user.to_dict()
    button_text = 'Нравится'
    photo_paths = post.photos_paths.split(' ')
    photo_paths.remove('')
    comment_form = AddCommentForm()
    if comment_form.validate_on_submit():
        comment = comment_form.content.data
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
    return render_template('post.html', post=post_, p_id=post_['id'], button_text=button_text,
                           paths=photo_paths, tags=session.query(Tag).all(), comment_form=comment_form,
                           author_name=author['name'], author_href=author['href'])

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
@app.route('/account')
def account():
    user_id = current_user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    nick_name = user.name
    photo = user.photo_path
    email = user.email
    # Егор, смерджи только liked_post и форму профиля
    liked_post = ''
    liked_posts = user.liked_posts
    print(liked_posts)
    db_sess.close()
    return render_template('profile.html', title='Ваш профиль', name=nick_name, email=email,
                           photo=photo, liked_posts=liked_posts)


@app.route('/profile_change')
def change_profile():
    form = changeProfileForm()
    user_id = current_user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    nick_name = user.name
    photo = user.photo_path
    email = user.email
    # Егор, смерджи только liked_post и форму профиля
    liked_posts = user.liked_posts
    print(liked_posts)
    db_sess.close()
    return render_template('change_profile.html', title='Ваш профиль', name=nick_name, email=email,
                           photo=photo, form=form, liked_posts=liked_posts)



@app.route('/author/<int:id>')
def author(id):
    session = db_session.create_session()
    user = session.query(User).get(id)
    name = user.name
    user_posts = user.posts
    session.close()
    print(user_posts)
    return render_template('users_profile.html', name=name, user_posts=user_posts)

@app.route('/tag/<id>')
def tag(id):
    s_form = SearchPostForm()
    session = db_session.create_session()
    posts = find_posts_by_tag(id)
    if request.method == 'POST':
        if s_form.validate_on_submit():
            text = s_form.title.data
            return redirect(f'/search/{text}')
    session.close()
    return render_template('tag_page.html', posts=posts, search_form=s_form,
                           tags=session.query(Tag).all())


def main():
    db_session.global_init('db/wikiforum.db')
    news_api.add_resource(PostResourse, '/posts/<int:post_id>')
    news_api.add_resource(PostListResource, '/posts')
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
