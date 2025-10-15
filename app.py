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

app.jinja_env.filters["any"] = any


# Front-end Handlers
@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
    else:
        username = None
    return render_template("index.html", username=username)


# @app.route("/addMatchTest")
# def testMatchAddition():
#     addScheduledMatch(
#         9999,
#         1,
#         CompLevel.QUALIFYING,
#         "2025caav_qm9999",
#         "Test Match 9999",
#         9991,
#         9992,
#         9993,
#         9994,
#         9995,
#         9996,
#     )
#     return "ok"


# @app.route("/getMatchTest")
# def testMatchGetting():
#     return getMatch(CompLevel.QUALIFYING, 9999, 1)


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
        results = getMatch(compLevel, matchNumber, setNumber)[-1]  # type: ignore
    except (IndexError, AttributeError) as err:
        # IndexError: No matches are found that match
        # AttributeError: compLevel is not set (is still "none")
        failed = True

    if failed or matchNumber == -1 or compLevel == "none" or setNumber == -1:
        return render_template("match/matchSelect.html", matches=sortMatches(getAllMatches()), matchNum=setNumber if (compLevel == CompLevel.PLAYOFF) else matchNumber, compLevel=compLevel if type(compLevel) is str else compLevel.value)  # type: ignore

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
        "match/match.html",
        teams=[redTeams, blueTeams],
        matchData=matchData,
        results=results,
    )


@app.route("/team")
def teamPage():
    try:
        team = int(request.args.get("team"))  # type: ignore
        results = getTeam(team)
    except TypeError as err:
        return render_template(
            "team/teamSelect.html", teams=sortTeams(getAllTeams()), team=-1
        )

    if results is None:
        return render_template(
            "team/teamSelect.html", teams=sortTeams(getAllTeams()), team=team
        )

    matches = getTeamMatches(team)
    teamResults = getTeamResults(team)
    stats = {
        "startPos": getAllStatsForCategory(teamResults, "startPos"),
        "autoLeave": getAllStatsForCategory(teamResults, "autoLeave"),
        "autoReefL1": getAllStatsForCategory(teamResults, "autoReef", 0),
        "autoReefL2": getAllStatsForCategory(teamResults, "autoReef", 1),
        "autoReefL3": getAllStatsForCategory(teamResults, "autoReef", 2),
        "autoReefL4": getAllStatsForCategory(teamResults, "autoReef", 3),
        "autoReefMiss": getAllStatsForCategory(teamResults, "autoReefMiss"),
        "teleReefL1": getAllStatsForCategory(teamResults, "teleReef", 0),
        "teleReefL2": getAllStatsForCategory(teamResults, "teleReef", 1),
        "teleReefL3": getAllStatsForCategory(teamResults, "teleReef", 2),
        "teleReefL4": getAllStatsForCategory(teamResults, "teleReef", 3),
        "teleReefMiss": getAllStatsForCategory(teamResults, "teleReefMiss"),
        "autoProcessor": getAllStatsForCategory(teamResults, "autoProcessor"),
        "autoProcessorMiss": getAllStatsForCategory(teamResults, "autoProcessorMiss"),
        "teleProcessor": getAllStatsForCategory(teamResults, "teleProcessor"),
        "teleProcessorMiss": getAllStatsForCategory(teamResults, "teleProcessorMiss"),
        "autoNet": getAllStatsForCategory(teamResults, "autoNet"),
        "autoNetMiss": getAllStatsForCategory(teamResults, "autoNetMiss"),
        "teleNet": getAllStatsForCategory(teamResults, "teleNet"),
        "teleNetMiss": getAllStatsForCategory(teamResults, "teleNetMiss"),
        "endPos": getAllStatsForCategory(teamResults, "endPos"),
        "attemptedEndPos": getAllStatsForCategory(teamResults, "attemptedEndPos"),
        "minorFouls": getAllStatsForCategory(teamResults, "minorFouls"),
        "majorFouls": getAllStatsForCategory(teamResults, "majorFouls"),
        "score": getAllStatsForCategory(teamResults, "score"),
    }
    return render_template(
        "team/team.html",
        team=results,
        matches=sortMatches(matches),
        stats=stats,
        keyDisplayNames=keyDisplayNames,
    )


@app.route("/team/rank")
def teamRankPage():
    key = request.args.get("category")
    stat = request.args.get("stat")
    isDict = stat == "highest" or stat == "lowest"
    sort = request.args.get("sort")
    sort = not sort == "ascending"
    reefLevel = request.args.get("reefLevel")
    reefLevel = 0 if not reefLevel else int(reefLevel)
    if (not key) or (not stat in STAT_CODES):
        options = {
            "Score Impact": "score,0",
            "Starting Position": "startPos,0",
            "Auto Leave": "autoLeave,0",
            "Reef Auto": "autoReef,0",
            "Reef Auto L1": "autoReef,0",
            "Reef Auto L2": "autoReef,1",
            "Reef Auto L3": "autoReef,2",
            "Reef Auto L4": "autoReef,3",
            "Reef Auto Missed": "autoReefMiss,0",
            "Reef Tele-Op": "teleReef,0",
            "Reef Tele-Op L1": "teleReef,0",
            "Reef Tele-Op L2": "teleReef,1",
            "Reef Tele-Op L3": "teleReef,2",
            "Reef Tele-Op L4": "teleReef,3",
            "Reef Tele-Op Missed": "teleReefMiss,0",
            "Processor Auto": "autoProcessor,0",
            "Processor Auto Missed": "autoProcessorMiss,0",
            "Processor Tele-Op": "teleProcessor,0",
            "Processor Tele-Op Missed": "teleProcessorMiss,0",
            "Net Auto": "autoNet,0",
            "Net Auto Missed": "autoNetMiss,0",
            "Net Tele-Op": "teleNet,0",
            "Net Tele-Op Missed": "teleNetMiss,0",
            "Ending Position": "endPos,0",
            "Attempted Ending Position": "attemptedEndPos,0",
            "Minor Fouls": "minorFouls,0",
            "Major Fouls": "majorFouls,0"
        }

        return render_template("strategy/team/teamRankSelect.html", options=options)
        # abort(400)
    return render_template(
        "strategy/team/teamRank.html",
        ranking=rankTeams(key, stat, sort, reefLevel),
        category=key,
        stat=stat,
        sort=sort,
        reefLevel=reefLevel,
        keyDisplayNames=keyDisplayNames,
        isDict=isDict,
    )


@app.route("/scoreAlliance")
def scoreAlliancePage():
    
    team1 = None
    team2 = None
    team3 = None
    stat = None
    try:
        team1 = int(request.args.get("team1"))  # type: ignore
    except TypeError:
        pass
    try:
        team2 = int(request.args.get("team2"))  # type: ignore
    except TypeError:
        pass
    try:
        team3 = int(request.args.get("team3"))  # type: ignore
    except TypeError:
        pass
    
    stat = request.args.get("stat")  # type: ignore
    
    if not stat or not team1 or not team2 or not team3:
        return render_template("strategy/predict/select.html",stat=stat,team1=team1,team2=team2,team3=team3,teams=sortTeams(getAllTeams()))
    
    stat = str(stat).lower()
    

    if stat not in ["mean","median","mode","highest","lowest"]:
        return render_template("strategy/predict/select.html",stat="none",team1=team1,team2=team2,team3=team3,teams=sortTeams(getAllTeams()))

    if stat == "mean" or stat == "median" or stat == "mode":
        
        calculateFunction = getMeanOfScoringCategory if stat == "mean" else getMedianOfScoringCategory if stat=="median" else getModeOfScoringCategory
        
        result = calculateAverageAllianceScore(team1, team2, team3,calculateFunction)
        if not result:
            return render_template("strategy/predict/select.html",stat=stat,team1=team1,team2=team2,team3=team3,teams=sortTeams(getAllTeams()))
        return render_template("strategy/predict/result.html",result=result,team1=team1,team2=team2,team3=team3)
    else:
        result = calculateMinMaxAllianceScore(team1, team2, team3, stat == "highest")
        if not result:
            return render_template("strategy/predict/select.html",stat=stat,team1=team1,team2=team2,team3=team3,teams=sortTeams(getAllTeams()))
        return render_template("strategy/predict/result.html",result=result,team1=team1,team2=team2,team3=team3)

@app.route("/strategy")
def strategyPage():
    return render_template("strategy/strategy.html")

# @app.route("/scoreRobotTest")
# def testRobotScorring():
#     scoreRobotInMatch(
#         9999,
#         1,
#         CompLevel.QUALIFYING,
#         Station.RED1,
#         StartingPosition.RED,
#         False,
#         [0, 0, 0, 4],
#         2,
#         [2, 4, 3, 1],
#         7,
#         0,
#         0,
#         1,
#         0,
#         0,
#         0,
#         3,
#         1,
#         EndPosition.DEEP,
#         EndPosition.DEEP,
#         1,
#         0,
#         "They did good :3",
#         "tonnieboy300",
#     )
#     scoreRobotInMatch(
#         9999,
#         1,
#         CompLevel.QUALIFYING,
#         Station.RED1,
#         StartingPosition.RED,
#         False,
#         [0, 0, 0, 4],
#         2,
#         [2, 4, 3, 1],
#         7,
#         0,
#         0,
#         1,
#         0,
#         0,
#         0,
#         3,
#         1,
#         EndPosition.DEEP,
#         EndPosition.DEEP,
#         1,
#         0,
#         "They did terrible >:(",
#         "magician357",
#     )
#     return "ok"


# @app.route("/calculateScoreTest")
# def testScoreCalc():
#     return str(
#         calculateScoreFromData(getMatch(CompLevel.QUALIFYING, 9999, 1)[0], Station.RED1)
#     )


# @app.route("/testDataGetting")
# def testDataGetting():
#     return addScheduleFromTBA("2025caav")


@app.route("/scheduleEvent", methods=["GET", "POST"])
def scheduleEventPage():
    if request.method == "POST":
        try:
            data = request.json
            event = str(data["code"])  # type: ignore
        except:
            abort(400)
        addScheduleFromTBA(event)
        addTeamsFromTBA(event)
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


# @app.route("/testTeamGetting")
# def testTeamGetting():
#     event = request.args.get("event")
#     if not event:
#         abort(400)
#     addTeamsFromTBA(event)
#     return "ok"


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
    return render_template("team/uploadImage.html", team=team)


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


@app.route("/team/scout", methods=["GET", "POST"])
def scoutTeam():
    if request.method == "POST":
        submission = request.json
        try:
            team = int(request.headers["Team"])  # type: ignore
            user = session["username"]  # type: ignore
        except TypeError as e:
            app.logger.warning(e)
            abort(400)
        pitScoutTeam(team, user, submission)
        return "ok"
    team = None
    try:
        team = int(request.args.get("team"))  # type: ignore
    except:
        pass
    return render_template("team/pitScout.html", team=team)


dontSummarize = frozenset(
    ["startPos","endPos","attemptedEndPos"]
)
@app.route("/team/summary")
def teamDataSummary():
    stat = request.args.get("stat")
    if not (
        (stat == "mean")
        or (stat == "median")
        or (stat == "mode")
        or (stat == "highest")
        or (stat == "lowest")
    ):
        abort(400)
    data = []
    teams = getAllTeams()
    if not teams:
        app.logger.error("Failed to summarize team stats: No teams found.")
        abort(500)
    method = (
        getMeanOfScoringCategory
        if stat == "mean"
        else (
            getMedianOfScoringCategory
            if stat == "median"
            else (
                getModeOfScoringCategory
                if stat == "mode"
                else (
                    getMatchWithHighestValue
                    if stat == "highest"
                    else getMatchWithLowestValue
                )
            )
        )
    )
    isAnObject: bool = stat == "highest" or stat == "lowest"
    matchViewer = url_for("renderMatch")
    for team in teams:
        data.append({"team": team["number"], "results": []})
        results = getTeamResults(team["number"])
        if not results:
            continue
        for key, result in results[0]["results"][0].items():
            if type(result) == str or key in dontSummarize:
                continue
            if type(result) == list:
                i = 0
                for level in result:
                    piece = method(results, key, i)
                    if isAnObject:
                        data[-1]["results"].append({f"{key}L{i+1}": piece["value"], "matchId": f"{matchViewer}?matchNum={piece['matchNumber']}&compLevel={piece['compLevel']}&setNum={piece['setNumber']}"})  # type: ignore
                    else:
                        data[-1]["results"].append({f"{key}L{i+1}": piece})
                    i += 1
            else:
                piece = method(results, key)
                if isAnObject:
                    data[-1]["results"].append({key: piece["value"], "matchId": f"{matchViewer}?matchNum={piece['matchNumber']}&compLevel={piece['compLevel']}&setNum={piece['setNumber']}"})  # type: ignore
                else:
                    data[-1]["results"].append({key: piece})
        data[-1]["results"].insert(0,data[-1]["results"].pop())
    return data

@app.route("/team/table")
def teamTable():
    stat = request.args.get("stat")
    if not (
        (stat == "mean")
        or (stat == "median")
        or (stat == "mode")
        or (stat == "highest")
        or (stat == "lowest")
    ):
        return render_template("strategy/team/tableSelect.html")
    links = (stat == "highest" or stat == "lowest")
    
    displayNames = {
        "score": "Score Impact",
        "autoLeave": "Auto Leave",
        "autoReefL1": "Reef Auto L1",
        "autoReefL2": "Reef Auto L2",
        "autoReefL3": "Reef Auto L3",
        "autoReefL4": "Reef Auto L4",
        "autoReefMiss": "Reef Auto Missed",
        "teleReefL1": "Reef Tele-Op L1",
        "teleReefL2": "Reef Tele-Op L2",
        "teleReefL3": "Reef Tele-Op L3",
        "teleReefL4": "Reef Tele-Op L4",
        "teleReefMiss": "Reef Tele-Op Missed",
        "autoProcessor": "Processor Auto",
        "autoProcessorMiss": "Processor Auto Missed",
        "teleProcessor": "Processor Tele-Op",
        "teleProcessorMiss": "Processor Tele-Op Missed",
        "autoNet": "Net Auto",
        "autoNetMiss": "Net Auto Missed",
        "teleNet": "Net Tele-Op",
        "teleNetMiss": "Net Tele-Op Missed",
        "minorFouls": "Minor Fouls",
        "majorFouls": "Major Fouls",
    }
    data = teamDataSummary()
    return render_template("strategy/team/table.html",displayNames=displayNames,data=data,links=links,stat=stat,)

# @app.route("/testTeamImage")
# def testTeamImage():
#     if request.args.get("notWorking"):
#         addTeamImage(
#             open(os.path.join(root, "static/javascript/match.js"), "rb").read(),
#             687,
#             "tonnieboy300",
#         )
#         return "an error should have occured"
#     addTeamImage(
#         open(os.path.join(root, "static/images/testImage.jpg"), "rb").read(),
#         687,
#         "tonnieboy300",
#     )
#     return "ok"


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
            error = "Couldn't log in: " + result
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
            created = True
        else:
            message = "User already exists."
    return render_template("auth/newUser.html", created=created, message=message)


@app.route("/submitScore", methods=["GET", "POST"])
def submitScorePage():
    try:
        matchVal = int(request.args.get("matchNumber"))  # type: ignore
        compLvl = request.args.get("compLevel")  # type: ignore
        setVal = int(request.args.get("setNumber"))  # type: ignore
        rbtStat = request.args.get("robotStation")  # type: ignore
        teamNum = int(request.args.get("team"))  # type: ignore
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
                submission["autoReefMiss"],  # int # type: ignore
                submission["teleReef"],  # array of four ints # type: ignore
                submission["teleReefMiss"],  # int # type: ignore
                submission["autoProcessor"],  # int # type: ignore
                submission["autoProcessorMiss"],  # int # type: ignore
                submission["teleProcessor"],  # int # type: ignore
                submission["teleProcessorMiss"],  # int # type: ignore
                submission["autoNet"],  # int # type: ignore
                submission["autoNetMiss"],  # int # type: ignore
                submission["teleNet"],  # int # type: ignore
                submission["teleNetMiss"],  # int # type: ignore
                submission["endPosSuccess"], # bool # type: ignore
                EndPosition(
                    int(
                        submission["attemptedEndPos"] # int between 0-3, though should be 2 or 3 # type: ignore
                    )  
                ),
                submission["minorFouls"],  # int # type: ignore
                submission["majorFouls"],  # int # type: ignore
                submission["comment"],  # str # type: ignore
                scout,  # str # type: ignore
            ):
                abort(400)
        except TypeError as err:
            app.logger.error(f"Error submitting match: {err}")
            abort(400)
    if compLvl == CompLevel.PLAYOFF.value:
        match = setVal
    else:
        match = matchVal
    
    cannedComments = [
        "Bad Driver",
        "Good Driver",
        "Mediocre Driver",
        "Missed a lot",
        "Focused on barge",
        "Robot broke",
        "Defense",
        "Has exactly two cameras and no more then five wires and less than 7 batteries"
    ]
    
    return render_template(
        "match/submit.html",
        match=match,
        compLvl=compLvl,
        rbtStat=rbtStat,
        teamNum=teamNum,
        setVal=setVal,
        matchVal=matchVal,
        cannedComments = cannedComments
    )


@app.route("/uploadData", methods=["GET", "POST"])
def uploadJSON():
    if request.method == "POST":
        try:
            data: dict = request.json  # type: ignore
            station = Station(data["station"])
            matchNum: int = data["matchNum"]
            compLevel = CompLevel(data["compLevel"])
            setNum: int = data["setNum"]
            results = data["data"]

            if not scoreRobotInMatch(
                matchNum,
                setNum,
                compLevel,
                station,
                StartingPosition(results["startPos"]),
                results["autoLeave"],
                results["autoReef"],
                results["autoReefMiss"],
                results["teleReef"],
                results["teleReefMiss"],
                results["autoProcessor"],
                results["autoProcessorMiss"],
                results["teleProcessor"],
                results["teleProcessorMiss"],
                results["autoNet"],
                results["autoNetMiss"],
                results["teleNet"],
                results["teleNetMiss"],
                results["endPosSuccess"],
                EndPosition(results["attemptedEndPos"]),
                results["minorFouls"],
                results["majorFouls"],
                results["comment"],
                str(session.get("username")),
            ):
                return "match not found", 404
        except Exception as e:
            app.logger.warning(e)
            abort(400)

    return render_template("uploadJSON.html")


curAwesome = 0


@app.route("/mr/harder")
def awesome():
    global curAwesome
    curAwesome = (curAwesome + 1) % 2
    return render_template("awesome.html", file="harder" + str(curAwesome + 1) + ".jpg")


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return render_template("auth/logout.html",logoutPageVariable=True)


@app.route("/manageUsers", methods=["GET", "POST"])
def userManagementPage():
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

@app.route("/team/table2")
def matchTable():
    matches = getAllMatches()
    results = []
    teams = []
    for match in matches:
        for section in ["red1","red2","red3","blue1","blue2","blue3"]:
            if section in match["results"]:
                for result in match["results"][section]:
                    result["team"] = match["teams"][section]
                    for i in range(4):
                        result["autoReefL"+str(i+1)] = result["autoReef"][i]
                        result["teleReefL"+str(i+1)] = result["teleReef"][i]
                    result["matchNumber"] = match["matchNumber"]
                    result["setNumber"] = match["setNumber"]
                    result["compLevel"] = match["compLevel"]
                    result["displayName"] = match["displayName"]
                    results.append(result)
                    if result["team"] not in teams:
                        teams.append(result["team"])
    
    displayNames = {
        "team":"Team",
        "displayName": "Display Name",
        "score": "Score Impact",
        "matchNumber": "Match Number",
        "setNumber": "Set Number",
        "compLevel": "Competition Level",
        "startPos": "Starting Position",
        "autoLeave": "Auto Leave",
        "autoReefL1": "Reef Auto L1",
        "autoReefL2": "Reef Auto L2",
        "autoReefL3": "Reef Auto L3",
        "autoReefL4": "Reef Auto L4",
        "autoReefMiss": "Reef Auto Missed",
        "teleReefL1": "Reef Tele-Op L1",
        "teleReefL2": "Reef Tele-Op L2",
        "teleReefL3": "Reef Tele-Op L3",
        "teleReefL4": "Reef Tele-Op L4",
        "teleReefMiss": "Reef Tele-Op Missed",
        "autoProcessor": "Processor Auto",
        "autoProcessorMiss": "Processor Auto Missed",
        "teleProcessor": "Processor Tele-Op",
        "teleProcessorMiss": "Processor Tele-Op Missed",
        "autoNet": "Net Auto",
        "autoNetMiss": "Net Auto Missed",
        "teleNet": "Net Tele-Op",
        "teleNetMiss": "Net Tele-Op Missed",
        "endPos": "Ending Position",
        "attemptedEndPos": "Attempted Ending Position",
        "minorFouls": "Minor Fouls",
        "majorFouls": "Major Fouls",
        "comment":"Comment"
    }
    
    return render_template("/strategy/match/table2.html",results=results,displayNames=displayNames,teams=teams)

@app.route("/about")
def aboutPage():
    return render_template("about.html")

freeEndpoints = frozenset(
    ["login", "newUserPage", "static", "index", "logout", "aboutPage", "awesome"]
)  # endpoints that shouldn't require signing in
adminEndpoints = frozenset(
    ["strategyPage","teamRankPage","teamTable","scoreAlliancePage","matchTable"]
)  # endpoints that require user be admin
@app.before_request
def before_request():
    # check login status
    if request.endpoint not in freeEndpoints and not isLoggedIn():
        return redirect(url_for("login", next=request.full_path))
    
    if request.endpoint in adminEndpoints and not isAdmin(session["username"]):
        app.logger.warning(
            f"User {session['username']} attempted to access {request.endpoint} without admin"
        )
        abort(403)


@app.errorhandler(HTTPException)
def pageNotFound(e):
    response = e.get_response()
    return render_template("error.html", code=e.code, name=e.name), e.code


if __name__ == "__main__":
    app.run(debug=True)
