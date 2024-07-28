from flask import Blueprint, request
from src.app import User, Post, db
from http import HTTPStatus
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import NotFound

app = Blueprint("post", __name__, url_prefix="/posts")


def _create_post(user_id):
    data = request.json

    post = Post(
        author_id=user_id,
        title=data["title"],
        body=data["body"],
    )
    db.session.add(post)
    db.session.commit()


@app.route("/")
def get_all_posts():
    query = db.select(Post)
    posts = db.session.execute(query).scalars()
    return [
        {
            "id": post.id,
            "author": post.author_id,
            "title": post.title,
            "body": post.body
        }
        for post in posts
    ]


@app.route("/<int:user_id>", methods=["POST"])
@jwt_required()
def create_post(user_id):
    data = request.json
    try:
        _create_post(user_id)
        return {"message": "Post created"}, HTTPStatus.CREATED
    except NotFound as err:
        return {"message": "Post não criado, author não encontrado na base de dados."}, HTTPStatus.NOT_FOUND


@app.route("/<int:post_id>")
def get_post(post_id):
    try:
        post = db.get_or_404(Post, post_id)
    except NotFound as err:
        return {"message": "Post não encontrado."}, HTTPStatus.NOT_FOUND

    return {
        "id": post.id,
        "author": post.author_id,
        "title": post.title,
        "body": post.body,
    }


@app.route("/<int:post_id>", methods=["PATCH", "PUT"])
@jwt_required()
def update_post(post_id):
    try:
        post = db.get_or_404(Post, post_id)
        data = request.json
    except NotFound as err:
        return {"message": "Post não encontrado."}, HTTPStatus.NOT_FOUND
    
    mapper = inspect(Post)
    for column in mapper.attrs:
        if column.key in data:
            setattr(post, column.key, data[column.key])
    db.session.commit()

    return {
        "id": post.id,
        "author": post.author_id,
        "title": post.title,
        "body": post.body,
    }


@app.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    try:
        post = db.get_or_404(Post, post_id)
    except NotFound as err:
        return {"message": "Post não encontrado."}, HTTPStatus.NOT_FOUND
    db.session.delete(post)
    db.session.commit()

    return "", HTTPStatus.NO_CONTENT
