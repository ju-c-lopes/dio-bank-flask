from flask import Blueprint, request
from src.models import User, db
from src.utils import requires_role
from src.app import bcrypt
from src.views.user import CreateUserSchema, UserSchema
from http import HTTPStatus
from marshmallow import ValidationError
from sqlalchemy import inspect, func
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import NotFound

app = Blueprint("user", __name__, url_prefix="/users")


def _create_user():
    user_schema = CreateUserSchema()

    try:
        data = user_schema.load(request.json)
    except ValidationError as exc:
        return exc.messages, HTTPStatus.UNPROCESSABLE_ENTITY

    user = User(
        username=data["username"],
        password=bcrypt.generate_password_hash(data["password"]),
        role_id=data["role_id"],
    )
    db.session.add(user)
    db.session.commit()
    return {"message": "User created!"}, HTTPStatus.CREATED


@jwt_required()
@requires_role("admin")
def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    users_schema = UserSchema(many=True)
    return users_schema.dump(users)


@app.route("/", methods=["GET", "POST"])
def handle_user():
    if request.method == "POST":
        return _create_user()
    else:
        return {"users": _list_users()}


@app.route("/<int:user_id>")
#@jwt_required()
def get_user(user_id):
    """User detail view.
    ---
    get:
      tags:
        - user
      summary: get an user
      description: get an user
      parameters:
        - in: path
          name: user_id
          schema: UserIdParameter
      responses:
        200:
          description: Successful operation
          content:
            application/json:
              schema: UserSchema
    """
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
    """User delete view.
    ---
    delete:
      tags:
        - user
      summary: delete an user
      description: delete an user
      parameters:
        - in: path
          name: user_id
          schema: UserIdParameter
      responses:
        204:
          description: Successful operation
        404:
          description: Not found user
    """
    try:
        user = db.get_or_404(User, user_id)
    except NotFound:
        return {"message": "Usuário não encontrado."}, HTTPStatus.NOT_FOUND
        
    db.session.delete(user)
    db.session.commit()
    
    return "", HTTPStatus.NO_CONTENT
