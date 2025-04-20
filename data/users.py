import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

association_table_1 = sqlalchemy.Table(
    'readers_to_posts',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('posts', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('posts.id')),
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')))

association_table_2 = sqlalchemy.Table(
    'likers_and_posts',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('posts', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('posts.id')),
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')))


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    photo_path = sqlalchemy.Column(sqlalchemy.String, default='static/image/profile_pictures/0.jpg')
    href = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    posts = orm.relationship("Post", back_populates='user')
    comments = orm.relationship("Comment", back_populates='user')
    read_posts = orm.relationship('Post', secondary='readers_to_posts', backref='users')
    liked_posts = orm.relationship('Post', secondary='likers_and_posts', backref='likers')


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __str__(self):
        return f'{self.name}'

    def to_dict(self):
        return {'id': self.id, 'name':self.name, 'href':self.href, }

