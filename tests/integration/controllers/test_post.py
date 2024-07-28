from http import HTTPStatus
from sqlalchemy import func, inspect
from src.app import Post, User, Role, db

def test_get_all_post_success(client, post):
    # Given
    
    # When
    response = client.get("/posts/")
    
    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == [
        {
            "author": post.author_id,
            "body": post.body,
            "id": post.id,
            "title": post.title
        }
    ]


def test_get_post_success(client, post):
    # Given
    
    # When
    response = client.get(f"/posts/{post.id}")
    
    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
            "author": post.author_id,
            "body": post.body,
            "id": post.id,
            "title": post.title
        }


def test_get_post_fail(client):
    # Given
    post_id = 2

    # When
    response = client.get(f"/posts/{post_id}")

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"message": "Post não encontrado."}
 
 
def test_create_post_success(client, user, access_token):
    # Given
    post = {"title": "Titulo novo post", "body": "Conteúdo novo post", "author_id": user.id}

    # When
    response = client.post(f"/posts/{user.id}", json=post, headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "Post created"}


def test_update_post_success(client, user, post, access_token):
    # Given
    post_up = {"title": "Titulo novo post", "body": "Conteúdo novo post", "author_id": user.id}

    # When
    response = client.patch(f"/posts/{user.id}", json=post_up, headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "id": 1,
        "author": user.id,
        "title": "Titulo novo post",
        "body": "Conteúdo novo post",
    }


def test_update_post_fail(client, post):
    # Given
    post_up = {"title": "Titulo novo post", "body": "Conteúdo novo post", "author_id": 1}

    # When
    response = client.patch(f"/posts/1", json=post_up)

    # Then
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Missing Authorization Header"}


def test_delete_post_success(client, user, post, access_token):
    # Given
    post_up = {"title": "Titulo novo post", "body": "Conteúdo novo post", "author_id": user.id}
    request = client.post(f"/posts/{user.id}", json=post_up, headers={"Authorization": f"Bearer {access_token}"})
    created_post = db.get_or_404(Post, post.id + 1)

    # When
    response = client.delete(f"/posts/{created_post.id}", json=post_up, headers={"Authorization": f"Bearer {access_token}"})

    # Then
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.json == None
