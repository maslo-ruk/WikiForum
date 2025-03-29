import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # theme = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')
    tags = orm.relationship("Tag",
                                  secondary="posts_to_tags",
                                  backref="posts")
    short = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # tags = orm.relationship(
    #     'Tag', secondary=post_to_tags,
    #     primaryjoin=(post_to_tags.c.posts == id),
    #     secondaryjoin=(post_to_tags.c.tags == id),
    #     backref=orm.backref('post_to_tags', lazy='dynamic'),
    #     lazy='dynamic'
    # )
    href = sqlalchemy.Column(sqlalchemy.String, nullable=True)
