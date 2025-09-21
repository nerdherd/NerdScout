import os
from flask import Flask, redirect, render_template, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
import certifi
from werkzeug.security import check_password_hash, generate_password_hash
import json
from bson import json_util, ObjectId
from pymongo import MongoClient
from enum import Enum
from typing import List


root = os.path.dirname(__file__)
app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config.from_mapping(
    SECRET_KEY=open(os.path.join(root, "secrets/secretKey"), "r").read()
)


class Station(Enum):
    RED1 = "red1"
    RED2 = "red2"
    RED3 = "red3"
    BLUE1 = "blue1"
    BLUE2 = "blue2"
    BLUE3 = "blue3"


class StartingPosition(Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3


class EndPosition(Enum):
    NONE = 0
    PARK = 1
    SHALLOW = 2
    DEEP = 3


# Initalize MongoDB Connection
client = MongoClient(
    open(os.path.join(root, "secrets/mongoDB"), "r").read(),
    # tlsCAFile=certifi.where(),
    connectTimeoutMS=30000,
    socketTimeoutMS=None,
    connect=False,
    maxPoolsize=1,
)
database = client.nerdScout
matches = database.matches
accounts = database.accounts


def addScheduledMatch(
    matchNumber: int,
    matchDesc: str,
    red1: int,
    red2: int,
    red3: int,
    blue1: int,
    blue2: int,
    blue3: int,
):
    matches.insert_one(
        {
            "matchNumber": matchNumber,
            "matchDesc": matchDesc,
            "teams": {
                "red1": red1,
                "red2": red2,
                "red3": red3,
                "blue1": blue1,
                "blue2": blue2,
                "blue3": blue3,
            },
            "results": {"scored": False},
        }
    )
    app.logger.info(f"New match scheduled: Match {matchNumber}, {matchDesc} between red alliance {red1}, {red2}, {red3} and blue alliance {blue1}, {blue2}, {blue3}.")


# This always outputs an array, in case there are multiple matches with the same number
def getMatchByNumber(matchNumber: int):
    results = matches.find({"matchNumber": matchNumber})
    parsedResults = parseResults(results)
    results.close()
    return parsedResults


def scoreRobotInMatch(
    matchNumber: int,
    station: Station,
    startPos: StartingPosition,
    autoLeave: bool,
    autoReef: List[int],
    teleReef: List[int],
    autoProcessor: int,
    teleProcessor: int,
    autoNet: int,
    teleNet: int,
    endPos: EndPosition,
    minorFouls: int,
    majorFouls: int,
    comment: str,
    scout: str,
):
    matches.update_many(
        {"matchNumber": matchNumber},
        {
            "$set": {
                "results."
                + station.value: {
                    "startPos": startPos.value,
                    "autoLeave": autoLeave,
                    "autoReef": autoReef,
                    "teleReef": teleReef,
                    "autoProcessor": autoProcessor,
                    "teleProcessor": teleProcessor,
                    "autoNet": autoNet,
                    "teleNet": teleNet,
                    "endPos": endPos.value,
                    "minorFouls": minorFouls,
                    "majorFouls": majorFouls,
                    "comment": comment,
                    "scout": scout,
                }
            }
        },
    )
    app.logger.info(f"Robot {startPos.value} scored for match {matchNumber} by {scout}.")


def calculateScore(
    autoLeave: bool,
    autoReef: List[int],
    teleReef: List[int],
    autoProcessor: int,
    teleProcessor: int,
    autoNet: int,
    teleNet: int,
    endPos: int,
    minorFouls: int,
    majorFouls: int,
):
    score = 0

    score += 3 if autoLeave else 0

    score += 3 * autoReef[0]
    score += 4 * autoReef[1]
    score += 6 * autoReef[2]
    score += 7 * autoReef[3]

    score += 2 * teleReef[0]
    score += 3 * teleReef[1]
    score += 4 * teleReef[2]
    score += 5 * teleReef[3]

    score += 6 * autoProcessor
    score += 6 * teleProcessor

    score += 4 * autoNet
    score += 4 * teleNet

    score += (
        2
        if endPos == EndPosition.PARK.value
        else (
            6
            if endPos == EndPosition.SHALLOW.value
            else 12 if endPos == EndPosition.DEEP.value else 0
        )
    )

    score -= 2 * minorFouls
    score -= 6 * majorFouls

    return score


def calculateScoreFromData(matchData: dict, team: Station):
    results = matchData["results"][team.value]
    score = calculateScore(
        results["autoLeave"],
        results["autoReef"],
        results["teleReef"],
        results["autoProcessor"],
        results["teleProcessor"],
        results["autoNet"],
        results["teleNet"],
        results["endPos"],
        results["minorFouls"],
        results["majorFouls"],
    )
    return score


# converts database results to JSON
# the default functions get stuck on ObjectID objects
def parseResults(data):
    return json.loads(json_util.dumps(data))


# Front-end Handlers
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/addMatchTest")
def testMatchAddition():
    addScheduledMatch(9999, "Test Match", 9991, 9992, 9993, 9994, 9995, 9996)
    return "ok"


@app.route("/getMatchTest")
def testMatchGetting():
    return getMatchByNumber(9999)


@app.route("/match")
def renderMatch():
    # TODO: make this take in data from URL
    teams = []
    results = getMatchByNumber(9999)[0]
    for team in results["teams"].keys():
        currentTeam = {
            "teamNumber": results["teams"][team],
            "hasData": (team in results["results"]),
        }

        if currentTeam["hasData"]:
            currentTeam["results"] = results["results"][team]

        teams.append(currentTeam)
    return render_template("match.html", teams=teams)


@app.route("/scoreRobotTest")
def testRobotScorring():
    scoreRobotInMatch(
        9999,
        Station.RED1,
        StartingPosition.BOTTOM,
        False,
        [0, 0, 0, 4],
        [2, 4, 3, 1],
        0,
        1,
        0,
        3,
        EndPosition.DEEP,
        1,
        0,
        "They did good :3",
        "tonnieboy300",
    )
    return "ok"


@app.route("/calculateScoreTest")
def testScoreCalc():
    return str(calculateScoreFromData(getMatchByNumber(9999)[0], Station.RED1))


def newUser(username: str, passwordHash: str):
    if getUser(username):
        app.logger.warning(f"Failed to create user {username} by {request.remote_addr}: User already exists.")
        return False
    accounts.insert_one(
        {
            "username": username,
            "passwordHash": passwordHash,
            "approved": False,
        }
    )
    app.logger.info(f"New user created: {username} by {request.remote_addr}.")
    return True


def getUser(username: str):
    user = accounts.find_one({"username": username})
    return user


def checkPassword(username:str, password:str):
    doc = getUser(username)
    try:
        if not doc["approved"]:  # type: ignore
            app.logger.warning(f"Unsuccessful login by {username} at {request.remote_addr}: Account not approved.")
            return False
        app.logger.info(f"Successful login by {username} at {request.remote_addr}.")
        return check_password_hash(doc["passwordHash"], password)  # type: ignore
    except TypeError:
        # if no users are found with a username, doc = None.
        app.logger.warning(f"Unsuccessful login by {username} at {request.remote_addr}: Incorrect password or account not found.")
        return False

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if checkPassword(username,password):
            session[username] = username
            return redirect("/", 302)
        else:
            error = "Couldn't log in."
    return render_template("login.html",error=error)

@app.route("/newUser", methods=["GET","POST"])
def newUserPage():
    message = None
    if request.method == "POST":
        if newUser(request.form["username"],generate_password_hash(request.form["password"])):
            message = "New unapproved user created!"
        else:
            message = "User already exists."
    return render_template("newUser.html",message=message)

if __name__ == "__main__":
    app.run(debug=True)
