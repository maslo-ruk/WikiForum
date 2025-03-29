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
    post.short = post.content[:SHORT_POST_LENGTH]
    post.user = sess.query(User).filter(User.id == user).first()
    post.href = f'/post/{len(sess.query(Post).all())+1}'
    sess.add(post)
    sess.commit()

def add_user(name, email, password):
    user = User()
    sess = db_session.create_session()
    if sess.query(User).filter(User.name == name).first() or sess.query(User).filter(User.email == email).first():
        return False
    if not check_password_safe(password):
        return False
    user.name = name
    user.email = email
    user.set_password(password)
    sess.add(user)
    sess.commit()
    sess.commit()


def add_tag(name):
    tag = Tag()
    tag.name = name
    sess = db_session.create_session()
    sess.add(tag)
    sess.commit()