from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.posts import Post
from flask import jsonify, send_file
from data.functions import captcha

from random import choice, randint
from io import BytesIO

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_news_not_found(post_id):
    session = db_session.create_session()
    posts = session.query(Post).get(post_id)
    if not posts:
        abort(404, message=f"Post {post_id} not found")

class CaptchaResource(Resource):
    def get(self, word):
        captcha(word)
        return send_file('materials/captcha_image.png', mimetype='image/png')


class Captchate(Resource):
    def get(self, word):
        captcha(word)
        return send_file('captcha_image.png', mimetype='image/png')
