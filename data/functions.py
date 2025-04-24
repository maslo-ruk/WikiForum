from data import db_session
from data.posts import Post
from data.users import User
from data.tags import Tag
from data.config import *


def check_pochta(email: str):
    if '@' in email:
        x = email.find('@')
        if '.' in email and email.rfind('.') > x:
            return True
        else:
            return False
    else:
        return False


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

def captcha(word):
    from PIL import Image, ImageDraw, ImageFont
    from random import choice, randint
    from io import BytesIO
    # символы для капчи выбираем с таким расчетом,
    # что бы посетители их не спутали с похожими
    # например букву `l` и цифру `1` легко спутать
    # генерация кода капчи из 5 символов
    code = word
    width = 200
    height = 100
    # создаем подложку
    img = Image.new('RGB', (width, height), (255, 255, 255))
    # получаем контекст рисования
    draw = ImageDraw.Draw(img)

    # Подключаем растровый шрифт (укажите свой)
    # начальное положение символов кода
    x = 0
    y = 12
    # наносим код капчи
    for let in code:
        if x == 0:
            x = 5
        else:
            x = x + width / 5
        # случайное положение по высоте
        y = randint(3, 55)
        # наносим символ
        draw.text((x, y), let, fill=(randint(0, 200), randint(0, 200), randint(0, 200), 128), font_size=700)

    # создаем шум капчи (в данном случае черточки)
    # можно создать шум точками (кому как нравится)
    for i in range(40):
        draw.line([(randint(0, width), randint(0, height)),
                   (randint(0, width), randint(0, height))],
                  randint(0, 200), 2, 128)

    # создаем объект в буфере
    f = BytesIO()
    # сохраняем капчу в буфер
    img.save('materials/captcha_image.png', "PNG")
    # возвращаем капчу как байтовый объект
    return f.getvalue()

def parse_post(content, post_id):
    counter = 0
    parsed = ''
    tag_opened = False
    tag = ''
    for i in content:
        if i == '<':
            parsed += '<br>'
            tag_opened = True
            continue
        if tag_opened:
            if i == '-':
               tag = '-'
               continue
            elif i == '>':
                tag_opened = False
                if tag == '-':
                    parsed += '<br>'
                else:
                    parsed += f'<img src="/static/image/post_pictures/{post_id}_{tag}"<br>'
        else:
            parsed += i
            counter += 1
            if counter == POST_LEN:
                counter = 0
                parsed+='\n'
    return parsed

