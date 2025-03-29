from data import db_session
from data.functions import add_user, add_tag, add_post
from data.posts import Post
from data.users import User
from data.tags import Tag

db_session.global_init('db/wikiforum.db')
# sess = db_session.create_session()
# add_user('default_user', 'Maslo.Paslo@yandex.ru', 'reS_et11')
# add_tag('physics')
# add_post('new rocket model', 'ELon mask made new rocket model, that will likely go to mars', [1], 1)
# print(sess.query(Post).first().href)
session = db_session.create_session()
post = session.query(Post).filter(Post.id == 1).first()
print(post.content)