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


def isLoggedIn() -> bool:
    """
    Checks if the user is logged in.
    
    Returns:
    - Boolean: User is logged in or not
    """
    return "username" in session


def newUser(username: str, passwordHash: str) -> bool:
    """
    Attempts to create a new unnaproved user.
    
    Logs an error if the username already exists.
    
    Inputs:
    - username (str): the username of the user
    - passwordHash (str): the hash of the user's password
    
    Returns:
    - Boolean: Whether or not the account was created successfully
    """
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
    """
    Checks if the password is correct for a user, and if the user is approved.
    
    Inputs:
    - username (str): the username of the user
    - password (str): the the user's password
    
    Returns:
    - Boolean: Password correct or not
    - String: Extra information ("Success" if successful, else reason for failure)
    """
    doc = getUser(username)
    try:
        if not doc["approved"]:  # type: ignore
            app.logger.warning(  # type: ignore
                f"Unsuccessful login by {username} at {request.remote_addr}: Account not approved."
            )
            return False, "Unapproved Account"
        result = check_password_hash(doc["passwordHash"], password)  # type: ignore
        if result:
            app.logger.info(f"Successful login by {username} at {request.remote_addr}.")  # type: ignore
            return True, "Success"
        else:
            app.logger.warning(  # type: ignore
                f"Unsuccessful login by {username} at {request.remote_addr}: Incorrect Password."
            )
            return False, "Incorrect Password"
    except TypeError:
        # if no users are found with a username, doc = None.
        app.logger.warning(  # type: ignore
            f"Unsuccessful login by {username} at {request.remote_addr}: Account not found."
        )
        return False, "Account not found"

def requestPasswordChange(username:str, passwordHash:str) -> bool:
    """
    Creates a new passwordChange in the requests database.

    Inputs:
    - username (str): the username of the user
    - passwordHash (str): the hash of the new password

    Returns:
    - Boolean: if it was succesful or not

    """
    app.logger.info(f"Password change for {username} requested by {request.remote_addr}")
    if not getUser(username):
        return False
    requestsDB.insert_one(
        {
            "type": "passwordChange",
            "data":{
                "username": username,
                "passwordHash": passwordHash,
            },
        }
    )
    return True

def getAllPasswordRequests() -> list:
    """
    Gets all password requests from the requests collection.

    Returns:
    - list: list of dicts of requests
    """
    results = requestsDB.find(
        {"type":"passwordChange"}
    )
    return parseResults(results)

def applyPasswordChange(id:str) -> bool:
    """
    Applies a password change request by ObjectId
    
    Inputs:
    - id (str): ObjectId str of request

    Returns:
    - bool: success
    """
    idParsed = ObjectId(id)
    result = parseResults(requestsDB.find_one({"_id": idParsed}))
    if not result:
        app.logger.error(f"Failed to apply password update for request {id}: request not found.")
        return False
    accounts.find_one_and_update(
        {"username": result["data"]["username"]},
        {"$set":{"passwordHash": result["data"]["passwordHash"]}}
    )
    requestsDB.find_one_and_delete({"_id": idParsed})
    app.logger.info(f"{request.cookies.get('username')} updated password for {result['data']['username']}.")
    return True