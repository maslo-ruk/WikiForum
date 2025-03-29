import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


association_table = sqlalchemy.Table(
    'posts_to_tags',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('posts', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('posts.id')),
    sqlalchemy.Column('tags', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tags.id')))


class Tag(SqlAlchemyBase):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)