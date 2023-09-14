import pytest

from org_chart_maker.db import get_db
from utils import *

def test_index(client, auth):
    # You must log in first, to get to the index page.
    # response = client.get("/")
    # assert b"Log In" in response.data
    # assert b"Register" in response.data

    auth.login()
    response = client.get("/new")
    assert b"Manage" in response.data


@pytest.mark.parametrize("path", ("/manage",))
def test_login_required(client, path):
    response = client.get(path)
    assert removeUrlPrefix(response.headers["Location"]) == "/auth/login"


def test_non_existing_diagram(client, auth):
    # Log in.
    auth.login()

    # Navigate to diagram that does not exist.
    diagramName = "dne"
    response = client.get("/?diagram=" + diagramName)

    # This should show a message.
    message = "Diagram " + diagramName + ".xml not found."
    assert bytes(message, 'utf-8') in response.data


# def test_non_existing_diagram_for_example_user(client, auth):
#     # TODO: Log in as example user.
#     # auth.loginAsExampleUser()
#
#     # Navigate to diagram that does not exist.
#     diagramName = "dne"
#     response = client.get("/?diagram=" + diagramName)
#
#     # This should not show a message. The example diagram should be loaded.
#     message = "Diagram " + diagramName + ".xml not found."
#     assert bytes(message, 'utf-8') not in response.data


# TODO: Use the test below for the "manage" page rename function.
# @pytest.mark.parametrize("path", ("/create", "/1/update"))
# def test_create_update_validate(client, auth, path):
#     auth.login()
#     response = client.post(path, data={"title": "", "body": ""})
#     assert b"Title is required." in response.data

# TODO: Now that the error handling is more robust, find a file that should
# not load at all.
# def test_invalid_file(client, auth):
#     # Log in.
#     auth.login()
#
#     # Navigate to diagram that does not exist.
#     diagramName = "invalid-file"
#     response = client.get("/?diagram=" + diagramName)
#
#     # This should show a message.
#     message = "Could not load diagram: "
#     assert bytes(message, 'utf-8') in response.data
