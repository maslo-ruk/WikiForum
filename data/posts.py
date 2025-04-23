import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from data.config import *
from data import db_session


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # theme = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    keywords = sqlalchemy.Column(sqlalchemy.String, default="")
    user = orm.relationship('User')
    tags = orm.relationship("Tag",
                                  secondary="posts_to_tags",
                                  backref="posts")
    photos_paths = sqlalchemy.Column(sqlalchemy.String, default='')
    first_photopath = sqlalchemy.Column(sqlalchemy.String, default='')
    short = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    href = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comments = orm.relationship("Comment", back_populates='post')

    def to_dict(self):
        return {'id': self.id,'title': self.title, 'content': self.content, 'user_id':self.user_id, 'views': self.views,
                'likes': self.likes}

    def set_values(self, title, content, tags, user):
        from data.users import User
        from data.tags import Tag
        self.title = title
        self.content = content
        sess = db_session.create_session()
        for i in tags:
            a = sess.query(Tag).filter(Tag.id == i).first()
            self.tags.append(a)
        if len(self.content) <= SHORT_POST_LENGTH:
            self.short = self.content
        else:
            self.short = self.content[:SHORT_POST_LENGTH] + '...'
        self.user = sess.query(User).filter(User.id == user).first()
        self.href = f'/post/{len(sess.query(Post).all()) + 1}'
        sess.commit()
        sess.close()
