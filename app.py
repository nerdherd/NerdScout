import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import certifi
from werkzeug.security import check_password_hash, generate_password_hash
import json
from bson import json_util, ObjectId
from pymongo import MongoClient


root = os.path.dirname(__file__)
app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


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

def addScheduledMatch(matchNumber: int, matchDesc: str, red1: int, red2: int, red3: int, blue1: int, blue2: int, blue3: int):
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
                "blue3": blue3
            },
            "results": {
                "scored": False
            }
        }
    )

def getMatchByNumber(matchNumber: int):
    results = matches.find(
        {"matchNumber": matchNumber}
    )
    return results


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
    addScheduledMatch(9999,"Test Match", 9991,9992,9993,9994,9995,9996)
    return "ok"

@app.route("/getMatchTest")
def testMatchGetting():
    return resultsToJSON(getMatchByNumber(9999))
    