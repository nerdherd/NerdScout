from array import array
from http.client import HTTPException
import os
import re
import filetype
import urllib.parse
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
from constants import *
from database import *
from auth import *


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config["JSON_SORT_KEYS"] = False

app.config.from_mapping(
    SECRET_KEY=open(os.path.join(root, "secrets/secretKey"), "r").read()
)


# Front-end Handlers
@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
    else:
        username = None
    return render_template("index.html", username=username)


@app.route("/addMatchTest")
def testMatchAddition():
    addScheduledMatch(
        9999,
        1,
        CompLevel.QUALIFYING,
        "2025caav_qm9999",
        "Test Match 9999",
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


@app.route("/match")
def renderMatch():
    matchNumber = -1
    compLevel = "none"
    setNumber = -1
    
    failed = False
    
    if "matchNum" in request.args:
        matchNumber = int(request.args.get("matchNum"))  # type: ignore
    
    if "compLevel" in request.args:
        compLevelString = request.args.get("compLevel")
        try:
            compLevel = CompLevel(compLevelString)  # type: ignore
        except ValueError:
            failed = True
        
    if "setNum" in request.args:
        setNumber = int(request.args.get("setNum"))  # type: ignore
    try:
        results = getMatch(compLevel, matchNumber, setNumber)[-1] # type: ignore
    except (IndexError,AttributeError) as err:
        # IndexError: No matches are found that match
        # AttributeError: compLevel is not set (is still "none")
        failed = True
    
    if failed or matchNumber == -1 or compLevel == "none" or setNumber == -1:
        return render_template("match/matchSelect.html", matches=sortMatches(getAllMatches()),matchNum=setNumber if (compLevel == CompLevel.PLAYOFF) else matchNumber,compLevel=compLevel if type(compLevel) is str else compLevel.value) # type: ignore

    # view test match with this link:
    # http://127.0.0.1:5000/match?matchNum=9999&compLevel=qm&setNum=1

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
                f"Team {results['teams'][team]} in match {compLevel}{matchNumber} set {setNumber} has no stored alliance."
            )
    return render_template(
        "match/match.html", teams=[redTeams, blueTeams], matchData=matchData
    )


@app.route("/team")
def teamPage():
    try:
        team = int(request.args.get("team"))  # type: ignore
        results = getTeam(team)
    except TypeError as err:
        return render_template("team/teamSelect.html", teams=sortTeams(getAllTeams()), team=-1)
    
    if results is None:
        return render_template("team/teamSelect.html", teams=sortTeams(getAllTeams()), team=team)
    
    matches = getTeamMatches(team)
    stats = {
        keyDisplayNames["startPos"]: getAllStatsForCategory(getTeamResults(team),"startPos"),
        keyDisplayNames["autoLeave"]: getAllStatsForCategory(getTeamResults(team),"autoLeave"),
        keyDisplayNames["autoReefL1"]: getAllStatsForCategory(getTeamResults(team),"autoReef",0),
        keyDisplayNames["autoReefL2"]: getAllStatsForCategory(getTeamResults(team),"autoReef",1),
        keyDisplayNames["autoReefL3"]: getAllStatsForCategory(getTeamResults(team),"autoReef",2),
        keyDisplayNames["autoReefL4"]: getAllStatsForCategory(getTeamResults(team),"autoReef",3),
        keyDisplayNames["autoReefMiss"]: getAllStatsForCategory(getTeamResults(team),"autoReefMiss"),
        keyDisplayNames["teleReefL1"]: getAllStatsForCategory(getTeamResults(team),"teleReef",0),
        keyDisplayNames["teleReefL2"]: getAllStatsForCategory(getTeamResults(team),"teleReef",1),
        keyDisplayNames["teleReefL3"]: getAllStatsForCategory(getTeamResults(team),"teleReef",2),
        keyDisplayNames["teleReefL4"]: getAllStatsForCategory(getTeamResults(team),"teleReef",3),
        keyDisplayNames["teleReefMiss"]: getAllStatsForCategory(getTeamResults(team),"teleReefMiss"),
        keyDisplayNames["autoProcessor"]: getAllStatsForCategory(getTeamResults(team),"autoProcessor"),
        keyDisplayNames["autoProcessorMiss"]: getAllStatsForCategory(getTeamResults(team),"autoProcessorMiss"),
        keyDisplayNames["teleProcessor"]: getAllStatsForCategory(getTeamResults(team),"teleProcessor"),
        keyDisplayNames["teleProcessorMiss"]: getAllStatsForCategory(getTeamResults(team),"teleProcessorMiss"),
        keyDisplayNames["autoNet"]: getAllStatsForCategory(getTeamResults(team),"autoNet"),
        keyDisplayNames["autoNetMiss"]: getAllStatsForCategory(getTeamResults(team),"autoNetMiss"),
        keyDisplayNames["teleNet"]: getAllStatsForCategory(getTeamResults(team),"teleNet"),
        keyDisplayNames["teleNetMiss"]: getAllStatsForCategory(getTeamResults(team),"teleNetMiss"),
        keyDisplayNames["endPos"]: getAllStatsForCategory(getTeamResults(team),"endPos"),
        keyDisplayNames["attemptedEndPos"]: getAllStatsForCategory(getTeamResults(team),"attemptedEndPos"),
        keyDisplayNames["minorFouls"]: getAllStatsForCategory(getTeamResults(team),"minorFouls"),
        keyDisplayNames["majorFouls"]: getAllStatsForCategory(getTeamResults(team),"majorFouls"),
        keyDisplayNames["score"]: getAllStatsForCategory(getTeamResults(team),"score"),
    }
    return render_template("team/team.html", team=results, matches=sortMatches(matches), stats=stats)

@app.route("/team/rank")
def teamRankPage():
    key = request.args.get("category")
    stat = request.args.get("stat")
    sort = request.args.get("sort")
    sort = not sort == "ascending"
    reefLevel = request.args.get("reefLevel")
    reefLevel = 0 if not reefLevel else int(reefLevel)
    if (not key) or (not stat in STAT_CODES):
        abort(400)
    return render_template("team/teamRank.html", ranking=rankTeams(key,stat,sort,reefLevel),category=key,stat=stat,sort=sort,reefLevel=reefLevel,keyDisplayNames=keyDisplayNames)
    


@app.route("/scoreRobotTest")
def testRobotScorring():
    scoreRobotInMatch(
        9999,
        1,
        CompLevel.QUALIFYING,
        Station.RED1,
        StartingPosition.RED,
        False,
        [0, 0, 0, 4],
        2,
        [2, 4, 3, 1],
        7,
        0,
        0,
        1,
        0,
        0,
        0,
        3,
        1,
        EndPosition.DEEP,
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
        StartingPosition.RED,
        False,
        [0, 0, 0, 4],
        2,
        [2, 4, 3, 1],
        7,
        0,
        0,
        1,
        0,
        0,
        0,
        3,
        1,
        EndPosition.DEEP,
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


@app.route("/scheduleEvent", methods=["GET", "POST"])
def scheduleEventPage():
    if request.method == "POST":
        try:
            data = request.json
            event = str(data["code"])  # type: ignore
        except:
            abort(400)
        addScheduleFromTBA(event)
    return render_template("match/schedule/addSchedule.html")


@app.route("/updateSchedule", methods=["GET", "POST"])
def updateSchedulePage():
    if request.method == "POST":
        try:
            data = request.json
            event = str(data["code"])  # type: ignore
        except:
            abort(400)
        updateScheduleFromTBA(event)
    return render_template("match/schedule/addSchedule.html")


@app.route("/testTeamGetting")
def testTeamGetting():
    event = request.args.get("event")
    if not event:
        abort(400)
    addTeamsFromTBA(event)
    return "ok"


@app.route("/team/addTeamImage", methods=["GET", "POST"])
def addTeamImagePage():
    if request.method == "POST":
        try:
            image = request.data
            addTeamImage(image, int(request.args.get("team")), session["username"])  # type: ignore
        except Exception as e:
            app.logger.warning(e)
            abort(400)
    team = 0
    try:
        team = int(request.args.get("team"))  # type: ignore
    except:
        pass
    return render_template("team/uploadImage.html",team=team)


@app.route("/team/addComment", methods=["GET", "POST"])
def setTeamComment():
    if request.method == "POST":
        submission = request.json
        try:
            team = int(submission["team"])  # type: ignore
            comment = submission["comment"]  # type: ignore
            user = session["username"]  # type: ignore
        except TypeError as e:
            app.logger.warning(e)
            abort(400)
        addComment(team, comment, user)
        return "ok"
    else:
        team = 0
        try:
            team = int(request.args.get("team"))  # type: ignore
        except:
            pass
        return render_template("team/addComment.html", team=team)


@app.route("/testTeamImage")
def testTeamImage():
    if request.args.get("notWorking"):
        addTeamImage(
            open(os.path.join(root, "static/javascript/match.js"), "rb").read(),
            687,
            "tonnieboy300",
        )
        return "an error should have occured"
    addTeamImage(
        open(os.path.join(root, "static/images/testImage.jpg"), "rb").read(),
        687,
        "tonnieboy300",
    )
    return "ok"


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    location = request.args.get("next")
    if isLoggedIn():
        return redirect(location if location else "/", 302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        successful, result = checkPassword(username, password)
        if successful:
            session["username"] = username
            location = request.args.get("next")
            return redirect(location if location else "/", 302)
        else:
            error = "Couldn't log in: "+result
    return render_template("auth/login.html", error=error)


@app.route("/newUser", methods=["GET", "POST"])
def newUserPage():
    message = None
    created = False
    if request.method == "POST":
        if newUser(
            request.form["username"], generate_password_hash(request.form["password"])
        ):
            message = "New unapproved user created!"
            created=True
        else:
            message = "User already exists."
    return render_template("auth/newUser.html",created=created, message=message)


@app.route("/submitScore", methods=["GET", "POST"])
def submitScorePage():
    try:
        matchVal = int(request.args.get("matchNumber"))  # type: ignore
        compLvl = (request.args.get("compLevel"))  # type: ignore
        setVal = int(request.args.get("setNumber"))  # type: ignore
        rbtStat = (request.args.get("robotStation")) #type: ignore
        teamNum = int(request.args.get("team")) #type: ignore
    except:
        return redirect(url_for("renderMatch"))
    if request.method == "POST":
        submission = request.json
        try:
            matchNumber = int(submission["matchNum"])  # type: ignore
            compLevel = CompLevel(submission["compLevel"])  # type: ignore
            setNumber = int(submission["setNum"])  # type: ignore
            currentRobot = Station(submission["robot"])  # type: ignore
            scout = session["username"]
        except TypeError as err:
            app.logger.error(f"Error submitting match: {err}")
            abort(400)
        try:
            if not scoreRobotInMatch(
                matchNumber,
                setNumber,
                compLevel,
                currentRobot,  # str
                StartingPosition(
                    int(submission["startPos"])  # int between 1-3 # type: ignore
                ),
                bool(submission["autoLeave"]),  # bool # type: ignore
                submission["autoReef"],  # array of four ints # type: ignore
                submission["autoReefMiss"], # int # type: ignore
                submission["teleReef"],  # array of four ints # type: ignore
                submission["teleReefMiss"], # int # type: ignore
                submission["autoProcessor"],  # int # type: ignore
                submission["autoProcessorMiss"], # int # type: ignore
                submission["teleProcessor"],  # int # type: ignore
                submission["teleProcessorMiss"], # int # type: ignore
                submission["autoNet"],  # int # type: ignore
                submission["autoNetMiss"], # int # type: ignore
                submission["teleNet"],  # int # type: ignore
                submission["teleNetMiss"], # int # type: ignore
                EndPosition(int(submission["endPos"])),  # int between 0-3 # type: ignore
                EndPosition(int(submission["attemptedEndPos"])), # int between 0-3, though should be 2 or 3 # type: ignore
                submission["minorFouls"],  # int # type: ignore
                submission["majorFouls"],  # int # type: ignore
                submission["comment"],  # str # type: ignore
                scout,  # str # type: ignore
            ):
                abort(400)
        except TypeError as err:
            app.logger.error(f"Error submitting match: {err}")
            abort(400)
    if (compLvl == CompLevel.PLAYOFF.value):
        match = setVal
    else:
        match = matchVal
    return render_template("match/submit.html",match=match,compLvl=compLvl,rbtStat=rbtStat,teamNum=teamNum,setVal=setVal, matchVal=matchVal)

curAwesome = 0
@app.route("/mr/harder")
def awesome():
    global curAwesome
    curAwesome=(curAwesome+1)%2
    return render_template("awesome.html",file="harder"+str(curAwesome+1)+".jpg")

@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return render_template("auth/logout.html")


@app.route("/manageUsers", methods=["GET", "POST"])
def userManagementPage():
    if not isAdmin(session["username"]):
        app.logger.warning(
            f"User {session['username']} attempted to access user management page."
        )
        abort(403)
    if request.method == "POST":
        try:
            data = request.json
            user: str = data["username"]  # type: ignore
            decision: bool = data["approved"]  # type: ignore
        except:
            app.logger.warning(
                f"User {session['username']} ({request.remote_addr}) failed to manage a user: Malformed Request."
            )
            abort(400)
        if isAdmin(user):
            app.logger.warning(
                f"User {session['username']} ({request.remote_addr}) failed to {'approve' if decision else 'unapprove'} {user}: User Is An Admin"
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
                f"User {session['username']} ({request.remote_addr}) failed to {'approve' if decision else 'unapprove'} {user}: User Does Not Exist"
            )
            abort(400)
        app.logger.info(
            f"User {session['username']} ({request.remote_addr}) {'approved' if decision else 'unapproved'} {user}."
        )
    return render_template("accountManagement.html", users=getAllUsers())

@app.route("/about")
def aboutPage():
    return render_template('about.html')


@app.before_request
def before_request():
    # check login status
    if request.endpoint not in freeEndpoints and not isLoggedIn():
        return redirect(
            url_for('login',next=request.path)
        )


@app.errorhandler(HTTPException)
def pageNotFound(e):
    response = e.get_response()
    return render_template("error.html", code=e.code, name=e.name), e.code


if __name__ == "__main__":
    app.run(debug=True)
