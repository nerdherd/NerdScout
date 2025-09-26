from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
    Blueprint,
)
from database import *


def isLoggedIn():
    return "username" in session


def newUser(username: str, passwordHash: str):
    if getUser(username):
        app.logger.warning(  # type: ignore
            f"Failed to create user {username} by {request.remote_addr}: User already exists."
        )
        return False
    accounts.insert_one(
        {
            "username": username,
            "passwordHash": passwordHash,
            "approved": False,
            "admin": False,
        }
    )
    app.logger.info(f"New user created: {username} by {request.remote_addr}.")  # type: ignore
    return True


def checkPassword(username: str, password: str):
    doc = getUser(username)
    try:
        if not doc["approved"]:  # type: ignore
            app.logger.warning(  # type: ignore
                f"Unsuccessful login by {username} at {request.remote_addr}: Account not approved."
            )
            return False
        result = check_password_hash(doc["passwordHash"], password)  # type: ignore
        if result:
            app.logger.info(f"Successful login by {username} at {request.remote_addr}.")  # type: ignore
        else:
            app.logger.warning(  # type: ignore
                f"Unsuccessful login by {username} at {request.remote_addr}: Incorrect Password."
            )
        return result
    except TypeError:
        # if no users are found with a username, doc = None.
        app.logger.warning(  # type: ignore
            f"Unsuccessful login by {username} at {request.remote_addr}: Account not found."
        )
        return False
