import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

association_table = sqlalchemy.Table(
    'readers_to_posts',
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

    posts = orm.relationship("Post", back_populates='user')
    comments = orm.relationship("Comment", back_populates='user')
    read_posts = orm.relationship('Post', secondary='readers_to_posts', backref='users')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


