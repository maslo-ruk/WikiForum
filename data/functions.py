from data import db_session
from data.posts import Post
from data.users import User
from data.tags import Tag
from data.config import *


def check_password_safe(password):
    return True


def add_post(title, content, tags, user):
    post = Post()
    post.title = title
    post.content = content
    sess = db_session.create_session()
    for i in tags:
        a = sess.query(Tag).filter(Tag.id == i).first()
        post.tags.append(a)
    if len(post.content) <= SHORT_POST_LENGTH:
        post.short = post.content
    else:
        post.short = post.content[:SHORT_POST_LENGTH] + '...'
    post.user = sess.query(User).filter(User.id == user).first()
    post.href = f'/post/{len(sess.query(Post).all())+1}'
    sess.add(post)
    sess.commit()
    return post

def add_user(name, email, password):
    user = User()
    sess = db_session.create_session()
    id = len(sess.query(User).all()) + 1
    if sess.query(User).filter(User.name == name).first() or sess.query(User).filter(User.email == email).first():
        return False
    if not check_password_safe(password):
        return False
    user.name = name
    user.email = email
    user.set_password(password)
    user.href = f'author/{id}'
    sess.add(user)
    sess.commit()
    sess.close()


def find_posts_by_tag(tag_id):
    sess = db_session.create_session()
    posts = sess.query(Post).filter(Post.tags.any(id=tag_id)).all()
    sess.close()
    return posts


def add_tag(name):
    tag = Tag()
    tag.name = name
    sess = db_session.create_session()
    tag.href = f'/tag/{len(sess.query(Tag).all()) + 1}'
    sess.add(tag)
    sess.commit()
    sess.close()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def allowed_file(filename):
    print(filename.rsplit('.', 1)[1])
    print('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS, 1)
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS