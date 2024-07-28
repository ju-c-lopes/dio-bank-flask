from flask import Blueprint, request
from src.app import User, db
from src.utils import requires_role
from http import HTTPStatus
from sqlalchemy import inspect, func
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import NotFound

app = Blueprint("user", __name__, url_prefix="/users")


def _create_user():
    data = request.json
    user = User(
        username=data["username"],
        password=data["password"],
        role_id=data["role_id"],
    )
    db.session.add(user)
    db.session.commit()


def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        {
            "user": user.id,
            "username": user.username,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
            }
        }
        for user in users
    ]


@app.route("/", methods=["GET", "POST"])
@jwt_required()
@requires_role("admin")
def handle_user():
    if request.method == "POST":
        _create_user()
        return {"message": "User created!"}, HTTPStatus.CREATED
    else:
        return {"users": _list_users()}


@app.route("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    try:
        user = db.get_or_404(User, user_id)
    except NotFound:
        return {"message": "Não encontrado"}, HTTPStatus.NOT_FOUND

    return {
        "id": user.id,
        "username": user.username,
    }


@app.route("/<int:user_id>", methods=["PATCH", "PUT"])
@jwt_required()
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.json

    #if "username" in data:
    #    user.username = data["username"]
    #    db.session.commit()

    mapper = inspect(User)
    for column in mapper.attrs:
        if column.key in data:
            setattr(user, column.key, data[column.key])
    db.session.commit()

    return {
        "id": user.id,
        "username": user.username,
        "role": {
            "id": user.role.id,
            "name": user.role.name,
        }
    }


@app.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        user = db.get_or_404(User, user_id)
    except NotFound:
        return {"message": "Usuário não encontrado."}, HTTPStatus.NOT_FOUND
        
    db.session.delete(user)
    db.session.commit()
    
    return "", HTTPStatus.NO_CONTENT
