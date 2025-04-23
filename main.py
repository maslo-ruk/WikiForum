import shutil


from flask import Flask, request, render_template, redirect, jsonify, make_response, session
from data.functions import *
from data.posts_api import PostResourse, PostListResource
from data.captcha_api import CaptchaResource
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
        if text in i.title or text in i.keywords.split(' '):
            right_posts.append(i)
        elif text in i.content:
            other_posts.append(i)
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
    from random import choice
    form = RegisterForm()
    db_sess = db_session.create_session()
    code = session.get('captcha_code', 0)
    print(not code)
    if not code:
        session['captcha_code'] = ''.join([choice('QERTYUPLKJHGFDSAZXCVBN23456789') for i in range(5)])
        code = session.get('captcha_code', 0)
    print(code)
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password1, password2 = form.password.data, form.second_password.data
            captcha_ = form.captchafield.data
            if db_sess.query(User).filter(User.email == email).first():
                return render_template('register.html', form=form, message='Такой пользователь уже есть!', word=code)
            if password1 != password2:
                return render_template('register.html', form=form, message='Пароли не совпадают!', word=code)
            print(captcha_, code)
            if captcha_ != code:
                return render_template('register.html', form=form, message='Капча введена неверно!', word=code)
            try:
                file = request.files['files']
                if file and allowed_file(file.filename):
                    add_user(name, email, password1)
                    db_sess = db_session.create_session()
                    user = db_sess.query(User).all()[-1]
                    photo = f'{user.id}.{file.filename.rsplit(".", 1)[1]}'
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/profile_pictures', photo))
                    user.photo_path = f'static/image/profile_pictures/{photo}'
                elif file:
                    return render_template('register.html', form=form, message=f'Неверный форма изображения.\nДопустимые форматы:\n{", ".join(ALLOWED_EXTENSIONS)}',
                                           word=code)
                else:
                    add_user(name, email, password1)
                    db_sess = db_session.create_session()
                    user = db_sess.query(User).all()[-1]
                    photo = STANDART_PHOTO
            except Exception:
                photo = STANDART_PHOTO
            login_user(user, remember=form.remember_me.data)
            session['captcha_code'] = 0
            db_sess.commit()
            db_sess.close()
            return redirect('/')
    db_sess.close()
    return render_template('register.html', form=form, word=code)


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
                        if count == 1:
                            post.first_photopath = f'{os.path.join(app.config["UPLOAD_FOLDER"])}/post_pictures/{post_id}_{count}.{file.filename.rsplit(".", 1)[1]}'
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
    liked = 0
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
        user = current_user.id
        cu = session.query(User).filter(User.id == current_user.id).first()
        read = cu.read_posts
        if post not in read:
            post.views += 1
            cu.read_posts.append(post)
        if post not in cu.liked_posts:
            button_text = 'Нравится'
            liked = 1
        else:
            button_text = 'Убрать из понравившегося'
            liked = 0
    else:
        user = 0
    post_ = post.to_dict()
    content = parse_post(post.content, post.id)
    comments = []
    for i in post.comments:
        comments.append((i.content, i.user.name, i.user.href))
    session.commit()
    session.close()
    return render_template('post.html', post=post_, content=content, p_id=post_['id'], button_text=button_text,
                           paths=photo_paths, tags=session.query(Tag).all(), comment_form=comment_form,
                           author_name=author['name'], author_href=author['href'], comments=comments,
                           user=user, liked=liked)

@app.route('/like', methods=['POST', 'GET'])
def like():
    if request.method == 'POST':
        print(1)
        if current_user.is_authenticated:
            print(2)
            res = request.json
            print(res)
            id = res['post']
            db_sess = db_session.create_session()
            post = db_sess.query(Post).filter(Post.id == id).first()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            if post not in user.liked_posts:
                user.liked_posts.append(post)
                post.likes += 1
                db_sess.commit()
                return {'success': True,'can_like': True, 'val':1}
            else:
                user.liked_posts.remove(post)
                post.likes -= 1
                db_sess.commit()
                return {'success': True, 'can_like': True, 'val': -1}
        else:
            return jsonify({'success': True,'can_like': False, 'val':1})

@app.route('/profile')
def account():
    user_id = current_user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    nick_name = user.name
    photo = user.photo_path
    email = user.email
    liked_posts = user.liked_posts
    print(liked_posts)
    db_sess.close()
    return render_template('profile.html', title='Ваш профиль', name=nick_name, email=email,
                           photo=photo, liked_posts=liked_posts)


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


@app.route('/ctest')
def ctest():
    from random import choice
    code = session.get('captcha_code', 0)
    print(code)
    print(not code)
    if code == 'no_code' or not code:
        session['captcha_code'] = ''.join([choice('QERTYUPLKJHGFDSAZXCVBN23456789') for i in range(5)])
    return render_template('ctest.html', word=code)


@app.route('/change_captcha_code', methods =['GET','POST'])
def ccode():
    if request.method == 'POST':
        a = request.json['code']
        session['captcha_code'] = a
    return {'success': True}


def main():
    db_session.global_init('db/wikiforum.db')
    news_api.add_resource(PostResourse, '/posts/<int:post_id>')
    news_api.add_resource(PostListResource, '/posts')
    news_api.add_resource(CaptchaResource, '/captcha.png/<word>')
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
