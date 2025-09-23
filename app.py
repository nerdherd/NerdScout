from array import array
from http.client import HTTPException
import os
import re
import urllib.parse
from flask import Flask, abort, redirect, render_template, request, session, url_for
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
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


STATION_LIST = [station.value for station in Station]


class StartingPosition(Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3


class EndPosition(Enum):
    NONE = 0
    PARK = 1
    SHALLOW = 2
    DEEP = 3


class CompLevel(Enum):
    QM = "qm"
    QUALIFYING = "qm"

    EF = "ef"

    QF = "qf"

    SF = "sf"
    PLAYOFF = "sf"

    F = "f"
    FINAL = "f"


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
teams = database.teams

TBA_KEY = open(os.path.join(root, "secrets/theBlueAlliance"), "r").read()


def addScheduledMatch(
    matchNumber: int,
    setNumber: int,
    compLevel: CompLevel,
    matchKey: str,
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
            "setNumber": setNumber,
            "compLevel": compLevel.value,
            "matchKey": matchKey,
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
    app.logger.info(
        f"New match scheduled: Match {compLevel}{matchNumber} between red alliance {red1}, {red2}, {red3} and blue alliance {blue1}, {blue2}, {blue3}."
    )


def addMatchFromTBA(match: dict):
    try:
        addScheduledMatch(
            match["match_number"],
            match["set_number"],
            CompLevel(match["comp_level"]),
            match["key"],
            int(match["alliances"]["red"]["team_keys"][0][3:]),
            int(match["alliances"]["red"]["team_keys"][1][3:]),
            int(match["alliances"]["red"]["team_keys"][2][3:]),
            int(match["alliances"]["blue"]["team_keys"][0][3:]),
            int(match["alliances"]["blue"]["team_keys"][1][3:]),
            int(match["alliances"]["blue"]["team_keys"][2][3:]),
        )
    except Exception as e:
        app.logger.error(
            f"Unable to load match from The Blue Alliance. Aborting. Error: {e}"
        )
        abort(500)


def addScheduleFromTBA(event: str):
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/matches/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        data = json.loads(data.text)
    except:
        app.logger.error(f"Failed to load match data for {event} from TBA.")
        abort(500)
    for match in data:
        addMatchFromTBA(match)
    return "ok"


def addTeam(number: int, longName: str, shortName: str, comment: str = ""):
    teams.insert_one(
        {
            "number": number,
            "longName": longName,
            "shortName": shortName,
            "comment": comment,
        }
    )


def addTeamsFromTBA(event: str):
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/teams/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        data = json.loads(data.text)
        if "Error" in data:
            app.logger.error(
                f"Failed to load team data for {event} from The Blue Alliance. API error: {data["Error"]}"
            )
            abort(500)
    except:
        app.logger.error(
            f"Failed to load team data for {event} from The Blue Alliance. Network error."
        )
        abort(500)
    for team in data:
        try:
            addTeam(
                int(team["team_number"]),
                team["name"],
                team["nickname"],
            )
        except Exception as e:
            app.logger.error(
                f"Failed to load team data for {event} from The Blue Alliance. {e}"
            )
            abort(500)


# This always outputs an array, in case there are multiple matches with the same number
def getMatch(compLevel: CompLevel, matchNumber: int, setNumber: int):
    results = matches.find(
        {
            "compLevel": compLevel.value,
            "matchNumber": matchNumber,
            "setNumber": setNumber,
        }
    )
    parsedResults = parseResults(results)
    results.close()
    return parsedResults


def scoreRobotInMatch(
    matchNumber: int,
    setNumber: int,
    compLevel: CompLevel,
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
    result = matches.update_many(
        {
            "matchNumber": matchNumber,
            "setNumber": setNumber,
            "compLevel": compLevel.value,
        },
        {
            "$push": {
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
    if result.matched_count == 0:
        app.logger.info(
            f"Failed to score robot {startPos.value} for match {matchNumber} by {scout}: Match does not exist."
        )
        return False
    app.logger.info(f"Robot {station.value} scored for match {matchNumber} by {scout}.")
    return True


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


def calculateScoreFromData(matchData: dict, team: Station, edit: int = -1):
    results = matchData["results"][team.value][edit]
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


def isLoggedIn():
    return "username" in session


def isAdmin(username: str):
    return parseResults(accounts.find_one({"username": username}))["admin"]


def getAllUsers():
    return parseResults(accounts.find({}))


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
    addScheduledMatch(
        9999,
        1,
        CompLevel.QUALIFYING,
        "2025caav_qm9999",
        9991,
        9992,
        9993,
        9994,
        9995,
        9996,
    )
    return "ok"


@app.route("/getMatchTest")
def testMatchGetting():
    return getMatch(CompLevel.QUALIFYING, 9999, 1)


# TODO: add all text descriptions for all match types
compLevelText = {"qm": "Qualifying", "sf": "Playoff", "f": "Final"}


@app.route("/match")
def renderMatch():
    try:
        matchNumber = int(request.args.get("matchNum"))  # type: ignore
        compLevel = CompLevel(request.args.get("compLevel"))  # type: ignore
        setNumber = int(request.args.get("setNum"))  # type: ignore
        results = getMatch(compLevel, matchNumber, setNumber)
    except:
        abort(400)
    redTeams = []
    blueTeams = []
    matchData = {
        "matchNumber": results["matchNumber"],
        "setNumber": results["setNumber"],
        "compLevel": compLevelText[results["compLevel"]],
    }
    for team in results["teams"].keys():
        currentTeam = {
            "teamNumber": results["teams"][team],
            "hasData": (team in results["results"]),
        }

        if currentTeam["hasData"]:
            currentTeam["results"] = results["results"][team]

        if "red" in team:
            redTeams.append(currentTeam)
        elif "blue" in team:
            blueTeams.append(currentTeam)
        else:
            app.logger.error(
                f"Team {results["teams"][team]} in match {compLevel}{matchNumber} set {setNumber} has no stored alliance."
            )
    return render_template(
        "match.html", teams=[redTeams, blueTeams], matchData=matchData
    )


@app.route("/scoreRobotTest")
def testRobotScorring():
    scoreRobotInMatch(
        9999,
        1,
        CompLevel.QUALIFYING,
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
    scoreRobotInMatch(
        9999,
        1,
        CompLevel.QUALIFYING,
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
        "They did terrible >:(",
        "magician357",
    )
    return "ok"


@app.route("/calculateScoreTest")
def testScoreCalc():
    return str(
        calculateScoreFromData(getMatch(CompLevel.QUALIFYING, 9999, 1)[0], Station.RED1)
    )


@app.route("/testDataGetting")
def testDataGetting():
    return addScheduleFromTBA("2025caav")


@app.route("/testTeamGetting")
def testTeamGetting():
    event = request.args.get("event")
    if not event:
        abort(400)
    addTeamsFromTBA(event)
    return "ok"


def newUser(username: str, passwordHash: str):
    if getUser(username):
        app.logger.warning(
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
    app.logger.info(f"New user created: {username} by {request.remote_addr}.")
    return True


def getUser(username: str):
    user = accounts.find_one({"username": username})
    return user


def checkPassword(username: str, password: str):
    doc = getUser(username)
    try:
        if not doc["approved"]:  # type: ignore
            app.logger.warning(
                f"Unsuccessful login by {username} at {request.remote_addr}: Account not approved."
            )
            return False
        result = check_password_hash(doc["passwordHash"], password)  # type: ignore
        if result:
            app.logger.info(f"Successful login by {username} at {request.remote_addr}.")
        else:
            app.logger.warning(
                f"Unsuccessful login by {username} at {request.remote_addr}: Incorrect Password."
            )
        return result
    except TypeError:
        # if no users are found with a username, doc = None.
        app.logger.warning(
            f"Unsuccessful login by {username} at {request.remote_addr}: Account not found."
        )
        return False


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    location = request.args.get("next")
    if isLoggedIn():
        return redirect(location if location else "/", 302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if checkPassword(username, password):
            session["username"] = username
            location = request.args.get("next")
            return redirect(location if location else "/", 302)
        else:
            error = "Couldn't log in."
    return render_template("auth/login.html", error=error)


@app.route("/newUser", methods=["GET", "POST"])
def newUserPage():
    message = None
    if request.method == "POST":
        if newUser(
            request.form["username"], generate_password_hash(request.form["password"])
        ):
            message = "New unapproved user created!"
        else:
            message = "User already exists."
    return render_template("newUser.html", message=message)


@app.route("/submitScore", methods=["GET", "POST"])
def submitScorePage():
    if request.method == "POST":
        submission = request.json
        try:
            matchNumber = submission["matchNum"]  # type: ignore
            compLevel = submission["compLevel"]  # type: ignore
            setNumber = submission["setNum"]  # type: ignore
            currentRobot = submission["robot"]  # type: ignore
        except:
            abort(400)
        try:
            if not scoreRobotInMatch(
                int(matchNumber),
                int(setNumber),
                CompLevel(compLevel),
                Station(currentRobot),  # str
                StartingPosition(
                    submission["startPos"] # int between 1-3 # type: ignore
                ),  
                submission["autoLeave"],  # bool # type: ignore
                submission["autoReef"],  # array of four ints # type: ignore
                submission["teleReef"],  # array of four ints # type: ignore
                submission["autoProcessor"],  # int # type: ignore
                submission["teleProcessor"],  # int # type: ignore
                submission["autoNet"],  # int # type: ignore
                submission["teleNet"],  # int # type: ignore
                EndPosition(submission["endPos"]),  # int between 0-3 # type: ignore
                submission["minorFouls"],  # int # type: ignore
                submission["majorFouls"],  # int # type: ignore
                submission["comment"],  # str # type: ignore
                submission["scout"],  # str # type: ignore
            ):
                abort(400)
        except:
            abort(400)
    return render_template("submit.html")


@app.route("/logout")
def logout():
    del session["username"]
    return "logged out"


@app.route("/manageUsers", methods=["GET", "POST"])
def userManagementPage():
    if not isAdmin(session["username"]):
        app.logger.warning(
            f"User {session["username"]} attempted to access user management page."
        )
        abort(401)
    if request.method == "POST":
        try:
            data = request.json
            user: str = data["username"]  # type: ignore
            decision: bool = data["approved"]  # type: ignore
        except:
            app.logger.warning(
                f"User {session["username"]} ({request.remote_addr}) failed to manage a user: Malformed Request."
            )
            abort(400)
        if isAdmin(user):
            app.logger.warning(
                f"User {session["username"]} ({request.remote_addr}) failed to {"approve" if decision else "unapprove"} {user}: User Is An Admin"
            )
            abort(401)
        result = accounts.update_one(
            {"username": user},
            {
                "$set": {
                    "approved": decision,
                }
            },
        )
        if result.matched_count == 0:
            app.logger.warning(
                f"User {session["username"]} ({request.remote_addr}) failed to {"approve" if decision else "unapprove"} {user}: User Does Not Exist"
            )
            abort(400)
        app.logger.info(
            f"User {session["username"]} ({request.remote_addr}) {"approved" if decision else "unapproved"} {user}."
        )
    return render_template("accountManagement.html", users=getAllUsers())


freeEndpoints = frozenset(
    ["login", "newUserPage", "static", "index"]
)  # endpoints that shouldn't require signing in


@app.before_request
def before_request():
    # check login status
    if request.endpoint not in freeEndpoints and not isLoggedIn():
        return redirect(
            f"{url_for('login')}?next={urllib.parse.quote(request.path, safe='')}"
        )


@app.errorhandler(HTTPException)
def pageNotFound(e):
    response = e.get_response()
    return render_template("error.html", code=e.code, name=e.name), e.code


if __name__ == "__main__":
    app.run(debug=True)
