import os
from flask import Flask
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


if __name__ == "__main__":
    app.run()

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


def getMatchByNumber(matchNumber: int):
    results = matches.find({"matchNumber": matchNumber})
    return results


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
                }
            }
        },
    )


# converts database results to JSON
# the default functions get stuck on ObjectID objects
def resultsToJSON(data):
    return json.loads(json_util.dumps(data))


# Front-end Handlers
@app.route("/")
def index():
    return "<p>It works!</p>"


@app.route("/addMatchTest")
def testMatchAddition():
    addScheduledMatch(9999, "Test Match", 9991, 9992, 9993, 9994, 9995, 9996)
    return "ok"


@app.route("/getMatchTest")
def testMatchGetting():
    matchResultCursor = getMatchByNumber(9999)
    results = resultsToJSON(matchResultCursor)
    matchResultCursor.close()
    return results


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
        EndPosition.SHALLOW,
        1,
        0,
        "They did good :3",
    )
    return "ok"
