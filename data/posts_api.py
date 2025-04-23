from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.posts import Post
from flask import jsonify

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

class PostResourse(Resource):
    def get(self, post_id):
        abort_if_news_not_found(post_id)
        sess = db_session.create_session()
        post = sess.query(Post).filter(Post.id == post_id).first()
        return jsonify({'post': post.to_dict()})

    def delete(self, post_id):
        abort_if_news_not_found(post_id)
        session = db_session.create_session()
        news = session.query(Post).get(post_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        post = session.query(Post).all()
        return jsonify({'post': [item.to_dict() for item in post]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['views'],
        )
        session.add(post)
        session.commit()
        return jsonify({'id': post.id})
