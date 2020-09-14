from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session
from starlette.testclient import TestClient

from app.db.models import UserDb
from app.server import app
from app.utils.security import hash_password
from tests.utils import reset_db

client = TestClient(app)


def setup_function():
    reset_db()


@db_session
def test_register():
    response = client.post(
        "/user/register",
        json={
            "username": "username",
            "email": "email@email.com",
            "password": "Abc123!67",
        },
    )
    assert response.status_code == 201
    assert orm.count(u for u in UserDb) == 1


def test_register_invalid_email():
    response = client.post(
        "/user/register",
        json={
            "username": "username",
            "email": "emailemail.com",
            "password": "Abc123!67",
        },
    )
    assert response.status_code == 422
    test = response.json()
    assert response.json()["detail"][0]["loc"] == ["body", "email"]


def test_register_invalid_password():
    response = client.post(
        "/user/register",
        json={
            "username": "username",
            "email": "email@email.com",
            "password": "Abc12367",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]


def test_register_invalid_username():
    response = client.post(
        "/user/register",
        json={"username": "", "email": "email@email.com", "password": "Abc123!67"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "username"]


def test_register_invalid_combined():
    response = client.post(
        "/user/register",
        json={
            "username": "username",
            "email": "emailemail.com",
            "password": "Abc12367",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "email"]
    assert response.json()["detail"][1]["loc"] == ["body", "password"]


@db_session
def test_register_existing():
    mixer.blend(UserDb, username="username")
    response = client.post(
        "/user/register",
        json={
            "username": "username",
            "email": "email@email.com",
            "password": "Abc123!67",
        },
    )
    assert response.status_code == 409
    assert orm.count(u for u in UserDb) == 1


@db_session
def test_login():
    user = mixer.blend(UserDb, password=hash_password("password"))
    response = client.post(
        "/user/login", data={"username": user.username, "password": "password"}
    )
    assert response.status_code == 200
    assert response.json()["token"]


@db_session
def test_login_invalid_credentials():
    user = mixer.blend(UserDb, password=hash_password("password"))
    response = client.post(
        "/user/login", data={"username": user.username, "password": "password2"}
    )
    assert response.status_code == 401
