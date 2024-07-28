from http import HTTPStatus
from sqlalchemy import func, inspect
from src.app import User, Role, db


def test_get_user_success(client, user, access_token):
    # Given

    # When
    response = client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"id": user.id, "username": user.username,}


def test_get_user_fail(client, access_token):
    # Given
    user_id = 2

    # When
    response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"message": "Não encontrado"}


def test_create_user(client, role, access_token):
    # Given
    payload = {"username": "usertest", "password": "user2", "role_id": role.id}

    # When
    response = client.post("/users/", json=payload, headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "User created!"}
    assert db.session.execute(db.select(func.count(User.id))).scalar() == 2


def test_list_users(client, user, access_token):
    # Given

    # When
    response = client.get("/users/", headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "users": [
            {
                "user": user.id,
                "username": user.username,
                "role": {
                    "id": user.role.id,
                    "name": user.role.name,
                }
            }
        ]
    }


def test_update_user_success(client, user, access_token):
    # Given
    payload = {"username": "usertest", "password": "user2"}

    # When
    response = client.patch(f"/users/{user.id}", json=payload, headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {'id': 1, 'role': {'id': 1, 'name': 'admin'}, 'username': 'usertest'}


def test_update_user_fail(client):
    # Given
    payload = {"username": "usertest", "password": "user2"}
    user_id = 1

    # When
    response = client.patch(f"/users/{user_id}", json=payload)

    # Then
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Missing Authorization Header"}


def test_delete_user_success(client, user, role, access_token):
    # Given
    payload = {"username": "usertest", "password": "user2", "role_id": role.id}
    request = client.post("/users/", json=payload, headers={"Authorization": f"Bearer {access_token}"})

    # When
    created_user = db.get_or_404(User, user.id + 1)
    response = client.delete(f"/users/{created_user.id}", headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.json == None
