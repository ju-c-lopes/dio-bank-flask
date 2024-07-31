import pytest
from src.app import create_app, db, User, Role, Post


@pytest.fixture()
def app():
    app = create_app(environment="testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def role(client):
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()

    return role


@pytest.fixture()
def user(client, role):
    user = User(username="john-doe", password="test", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture()
def access_token(client, user):
    response = client.post("/auth/login", json={"username": user.username, "password": user.password})
    return response.json["access_token"]


@pytest.fixture()
def post(client, user):
    post = Post(title="Titulo do post", body="Conteúdo do post.", author_id=user.id)
    db.session.add(post)
    db.session.commit()
    
    return post
