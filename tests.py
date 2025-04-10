from data import db_session
from data.functions import add_user, add_tag, add_post
from data.posts import Post
from data.users import User
from data.tags import Tag

def make_db():
    db_session.global_init('db/wikiforum.db')
    add_user('default_user', 'Maslo.Paslo@gmail.com', 'reset')
    for i in range(1,4):
        add_tag(f'default_tag_{i}')
    t = [[1], [2], [3], [3,1], [2,1], [2,3], [2]]
    c = 0
    for i in t:
        ix = map(str, i)
        add_post(f'test_post_{c}, tags: {" ".join(ix) }', f'testposttext_{c}', i, 1)
        c += 1
    sess = db_session.create_session()
    posts = sess.query(Tag).all()
    c = 1
    for i in posts:
        i.href = f'/tag/{c}'
        c += 1
        print(i.href)

def main():
    db_session.global_init('db/wikiforum.db')
    d = db_session.create_session()
    print(d.query(User).first().email)

main()

# new rocket model, tags: 1
# test_post_0, tags: 1
# test_post_1, tags: 2
# test_post_2, tags: 3
# test_post_3, tags: 3 1
# test_post_4, tags: 2 1
# test_post_5, tags: 2 3
# test_post_6, tags: 2
