import requests

from flask import (Flask, render_template, request,
                   session, url_for, redirect)
from PIL import Image, ImageDraw, ImageFont
from random import choice, randint
from io import BytesIO
from os import urandom
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

def captcha(width=200, height=100):
    # символы для капчи выбираем с таким расчетом,
    # что бы посетители их не спутали с похожими
    # например букву `l` и цифру `1` легко спутать
    # генерация кода капчи из 5 символов
    code = ''.join([choice('QWERTYUPLKJHGFDSAZXCVBN23456789') for i in range(5)])

    # создаем подложку
    img = Image.new('RGB', (width,height), (255,255,255))
    # получаем контекст рисования
    draw = ImageDraw.Draw(img)

    # Подключаем растровый шрифт (укажите свой)
    # начальное положение символов кода
    x=0
    y=12
    # наносим код капчи
    for let in code:
        if x == 0: x = 5
        else: x = x + width/5
        # случайное положение по высоте
        y = randint(3,55)
        # наносим символ
        draw.text((x,y), let, fill=(randint(0,200), randint(0,200), randint(0,200), 128), font_size=50)

    # создаем шум капчи (в данном случае черточки)
    # можно создать шум точками (кому как нравится)
    for i in range(40):
        draw.line([(randint(0,width),randint(0,height)),
                   (randint(0,width),randint(0,height))],
                  randint(0, 200), 2, 128)

    # создаем объект в буфере
    f = BytesIO()
    # сохраняем капчу в буфер
    img.save('imgd.png', "PNG")
    # возвращаем капчу как байтовый объект
    return  f.getvalue()

def main():
    make_db()

main()

# new rocket model, tags: 1
# test_post_0, tags: 1
# test_post_1, tags: 2
# test_post_2, tags: 3
# test_post_3, tags: 3 1
# test_post_4, tags: 2 1
# test_post_5, tags: 2 3
# test_post_6, tags: 2
