import pytest
from flask import g
from flask import session

from org_chart_maker.db import get_db
from utils import *

def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a", "email": "a"})
    assert removeUrlPrefix(response.headers["Location"]) == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
        ("username with spaces", "test", b"Username is invalid."),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password, "email": "a"}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert removeUrlPrefix(response.headers["Location"]) == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/new")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username or password."), ("test", "a", b"Incorrect username or password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session


def test_invalid_reset_link(client, auth):
    # log in.
    client.get("/auth/login")
    auth.login()

    # Try invalid link.
    response = client.get("/auth/reset-password?link=dne")

    # Check output.
    message = b"Invalid Reset Link"
    assert (message in response.data)
