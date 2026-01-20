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
import random
from bson import json_util, ObjectId
from pymongo import MongoClient
from enum import Enum
from typing import List
from constants import *
from database import *
from auth import *
from games import *

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config["JSON_SORT_KEYS"] = False

app.config.from_mapping(
    SECRET_KEY=open(os.path.join(root, "secrets/secretKey"), "r").read()
)

app.jinja_env.filters["any"] = any

game = Rebuilt(matches, teams)


# Front-end Handlers
@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
    else:
        username = None
    return render_template("index.html", username=username)

@app.route("/createTestMatches")
def createTestMatches():
    foundationNames = (
        "Abaca",
        "Louis & Lewis",
        "Super Evil Wevils",
        "Wheler",
        "Mr. Hello's",
        "John"
    )
    for i,foundationName in zip(range(9991,9997),foundationNames):
        if not getTeam(i):
            addTeam(i, f"{foundationName} Foundation", foundationName)
    for i in range(9991,9996):
        if not getMatch(CompLevel.QM, i, 1):
            addScheduledMatch(i,1,CompLevel.QM,f"2026test_qm{i}",f"TestMatch {i}", 9991,9992,9993,9994,9995,9996)
    randomScoringPeriods = lambda n: [{"time":random.random()*5.0,"scored":random.randint(0,30),"missed":random.randint(0,30)} for _ in range(n)]
    for i in range(9991,9996):
        for team in Station:
            game.scoreRobotInMatch(
                matchNumber=i,
                setNumber=1,
                compLevel=CompLevel.QM,
                station=team,
                startPos=random.random(),
                preloadFuel=random.randint(0,8),
                autoFuel=randomScoringPeriods(random.randint(0,5)),
                autoDepot=random.random()>0.5,
                autoBump=random.random()>0.5,
                autoTrench=random.random()>0.5,
                autoNeutralIntake=random.random()>0.5,
                autoAttemptedSecondScore=random.random()>0.5,
                autoSucceededSecondScore=random.random()>0.5,
                autoClimbAttempted=random.random()>0.5,
                autoClimbSuccess=random.random()>0.5,
                autoOutpostFeed=random.random()>0.5,
                firstShift=random.random()>0.5,
                transitionFuel=randomScoringPeriods(random.randint(0,5)),
                transitionFed=random.random()>0.5,
                transitionDefense=random.random()>0.5,
                firstActiveShiftFuel=randomScoringPeriods(random.randint(0,5)),
                firstActiveShiftFed=random.random()>0.5,
                firstActiveShiftDefense=random.random()>0.5,
                secondActiveShiftFuel=randomScoringPeriods(random.randint(0,5)),
                secondActiveShiftFed=random.random()>0.5,
                secondActiveShiftDefense=random.random()>0.5,
                firstInactiveShiftScored=random.random()>0.5,
                firstInactiveShiftFed=random.random()>0.5,
                firstInactiveShiftDefense=random.random()>0.5,
                secondInactiveShiftScored=random.random()>0.5,
                secondInactiveShiftFed=random.random()>0.5,
                secondInactiveShiftDefense=random.random()>0.5,
                endgameFuel=randomScoringPeriods(random.randint(0,5)),
                endgameFed=random.random()>0.5,
                endgameDefense=random.random()>0.5,
                endClimb=EndPositionRebuilt(random.randint(0,3)),
                outpostIntake=random.random()>0.5,
                groundIntake=random.random()>0.5,
                fedToOutpost=random.random()>0.5,
                minorFouls=random.randint(0,10),
                majorFouls=random.randint(0,3),
                comment="abaca",
                cannedComments=[],
                scout=random.choice(["hello","hello2","hlelo3","tonnieboy300","mr hello","hello jr","ms hello"])
            )
    return "ok."


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

    nextMatch = False
    try:
        getMatch(compLevel, matchNumber + 1, setNumber)[-1]  # type: ignore
        nextMatch = True
    except (IndexError, AttributeError) as err:
        # IndexError: There isnt a next match
        pass

    return render_template(
        "match/match.html",
        teams=[redTeams, blueTeams],
        matchData=matchData,
        results=results,
        nextMatch=nextMatch,
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
    stats = game.getAllStats(team)
    return render_template(
        "team/team.html",
        team=results,
        matches=sortMatches(matches),
        stats=stats,
        keyDisplayNames=game.keyDisplayNames,
        autoCapabilities=game.pitScoutAutoCapabilities, 
        teleCapabilities=game.pitScoutTeleCapabilities
    )


@app.route("/strategy/rank")
def teamRankPage():
    key = request.args.get("category")
    stat = request.args.get("stat")
    isDict = stat == "highest" or stat == "lowest"
    sort = request.args.get("sort")
    sort = not sort == "ascending"
    index = request.args.get("index")
    index = 0 if not index else int(index)
    if (not key) or (not stat in STAT_CODES):
        options = game.teamRankOptions

        return render_template("strategy/team/teamRankSelect.html", options=options)
        # abort(400)
    return render_template(
        "strategy/team/teamRank.html",
        ranking=rankTeams(key, stat, sort, index),
        category=key,
        stat=stat,
        sort=sort,
        index=index,
        keyDisplayNames=game.keyDisplayNames,
        isDict=isDict,
    )


@app.route("/strategy/scoreAlliance")
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
        return render_template(
            "strategy/predict/select.html",
            stat=stat,
            team1=team1,
            team2=team2,
            team3=team3,
            teams=sortTeams(getAllTeams()),
        )

    stat = str(stat).lower()

    if stat not in ["mean", "median", "mode", "highest", "lowest"]:
        return render_template(
            "strategy/predict/select.html",
            stat="none",
            team1=team1,
            team2=team2,
            team3=team3,
            teams=sortTeams(getAllTeams()),
        )

    if stat == "mean" or stat == "median" or stat == "mode":

        calculateFunction = (
            getMeanOfScoringCategory
            if stat == "mean"
            else (
                getMedianOfScoringCategory
                if stat == "median"
                else getModeOfScoringCategory
            )
        )

        result = game.calculateAverageAllianceScore(
            team1, team2, team3, calculateFunction
        )
        if not result:
            return render_template(
                "strategy/predict/select.html",
                stat=stat,
                team1=team1,
                team2=team2,
                team3=team3,
                teams=sortTeams(getAllTeams()),
            )
        return render_template(
            "strategy/predict/result.html",
            result=result,
            team1=team1,
            team2=team2,
            team3=team3,
        )
    else:
        result = game.calculateMinMaxAllianceScore(
            team1, team2, team3, stat == "highest"
        )
        if not result:
            return render_template(
                "strategy/predict/select.html",
                stat=stat,
                team1=team1,
                team2=team2,
                team3=team3,
                teams=sortTeams(getAllTeams()),
            )
        return render_template(
            "strategy/predict/result.html",
            result=result,
            team1=team1,
            team2=team2,
            team3=team3,
        )


@app.route("/strategy")
def strategyPage():
    return render_template("strategy/strategy.html")


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
        pitScoutTeam(team, user, submission)  # type: ignore
        return "ok"
    team = None
    try:
        team = int(request.args.get("team"))  # type: ignore
    except:
        pass
    # autoCapabilities = (
    #     ("Score in hub","auto-fuel"),
    #     ("Intake from depot","auto-depot"),
    #     ("Intake from outpost chute","auto-outpost"),
    #     ("Intake from neutral zone","auto-neutral"),
    #     ("Climb level 1 in the center","auto-climb1-center"),
    #     ("Climb level 1 on the sides","auto-climb1-side"),
    #     ("Climb level 1 in the inside","auto-climb1-inside"),
    # )
    # teleCapabilities = (
    #     ("Score in hub","tele-fuel"),
    #     ("Intake from depot","tele-depot"),
    #     ("Intake from outpost chute","tele-outpost"),
    #     ("Intake from neutral zone","tele-neutral"),
    #     ("Climb level 1 in the center","tele-climb1-center"),
    #     ("Climb level 1 on the sides","tele-climb1-side"),
    #     ("Climb level 1 in the inside","tele-climb1-inside"),
    #     ("Climb level 2 in the center","tele-climb2-center"),
    #     ("Climb level 2 on the sides","tele-climb2-side"),
    #     ("Climb level 2 in the inside","tele-climb2-inside"),
    #     ("Climb level 3 in the center","tele-climb3-center"),
    #     ("Climb level 3 on the sides","tele-climb3-side"),
    #     ("Climb level 3 in the inside","tele-climb3-inside"),
    # )
    return render_template("team/pitScout.html", team=team, autoCapabilities=game.pitScoutAutoCapabilities, teleCapabilities=game.pitScoutTeleCapabilities)


dontSummarize = frozenset(
    ["startPos", "endPos", "attemptedEndPos", "cannedComments", "endPosSuccess"]
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
        data[-1]["results"].insert(0, data[-1]["results"].pop())
    return data


@app.route("/strategy/teamtable")
def teamTable():
    # return "not implemented"
    stat = request.args.get("stat")
    if not (
        (stat == "mean")
        or (stat == "median")
        or (stat == "mode")
        or (stat == "highest")
        or (stat == "lowest")
    ):
        return render_template("strategy/team/tableSelect.html")
    links = stat == "highest" or stat == "lowest"

    displayNames = game.teamTableDisplayNames
    data = teamDataSummary()
    print(data)
    return render_template(
        "strategy/team/table.html",
        displayNames=displayNames,
        data=data,
        links=links,
        stat=stat,
    )


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


@app.route("/passwordRequest", methods=["GET", "POST"])
def passwordRequestPage():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if requestPasswordChange(username, generate_password_hash(password)):
            error = f"Request for {username} submitted."
        else:
            error = f"User {username} doesn't exist."
    return render_template("auth/passwordRequest.html", error=error)


@app.route("/resetPasswords", methods=["GET", "POST"])
def resetPasswordsPage():
    # applyPasswordChange("69176e12d48220b435ba6012")
    if request.method == "POST":
        data = request.json
        if not data:
            app.logger.warning(
                f"Failed to apply password change request: no data sent."
            )
            abort(400)
        try:
            if data["approved"]:
                applyPasswordChange(data["id"])
            else:
                deletePasswordChange(data["id"])
        except Exception as e:
            app.logger.warning(
                f"Failed to apply password change request: fields missing."
            )
            abort(400)
    return render_template(
        "auth/resetPasswords.html", requests=getAllPasswordRequests()
    )


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
            if not game.scoreRobotInMatch(
                matchNumber=matchNumber,
                setNumber=setNumber,
                compLevel=compLevel,
                station=currentRobot,  # str
                startPos=submission["startPos"],
                preloadFuel=submission["preloadFuel"],
                autoFuel=submission["autoFuel"],
                autoDepot=submission["autoDepot"],
                autoBump=submission["autoBump"],
                autoTrench=submission["autoTrench"],
                autoNeutralIntake=submission["autoNeutralIntake"],
                autoAttemptedSecondScore=submission["autoAttemptedSecondScore"],
                autoSucceededSecondScore=submission["autoSucceededSecondScore"],
                autoClimbAttempted=submission["autoClimbAttempted"],
                autoClimbSuccess=submission["autoClimbSuccess"],
                autoOutpostFeed=submission["autoOutpostFeed"],
                firstShift=submission["firstShift"],
                transitionFuel=submission["transitionFuel"],
                transitionFed=submission["transitionFed"],
                transitionDefense=submission["transitionDefense"],
                firstActiveShiftFuel=submission["firstActiveShiftFuel"],
                firstActiveShiftFed=submission["firstActiveShiftFed"],
                firstActiveShiftDefense=submission["firstActiveShiftDefense"],
                secondActiveShiftFuel=submission["secondActiveShiftFuel"],
                secondActiveShiftFed=submission["secondActiveShiftFed"],
                secondActiveShiftDefense=submission["secondActiveShiftDefense"],
                firstInactiveShiftScored=submission["firstInactiveShiftScored"],
                firstInactiveShiftFed=submission["firstInactiveShiftFed"],
                firstInactiveShiftDefense=submission["firstInactiveShiftDefense"],
                secondInactiveShiftScored=submission["secondInactiveShiftScored"],
                secondInactiveShiftFed=submission["secondInactiveShiftFed"],
                secondInactiveShiftDefense=submission["secondInactiveShiftDefense"],
                endgameFuel=submission["endgameFuel"],
                endgameFed=submission["endgameFed"],
                endgameDefense=submission["endgameDefense"],
                endClimb=EndPositionRebuilt(
                    int(
                        submission[ # int between 0-3, though should be 2 or 3 # type: ignore
                            "endClimb"
                        ]  
                    )
                ),
                outpostIntake=submission["outpostIntake"],
                groundIntake=submission["groundIntake"],
                fedToOutpost=submission["fedToOutpost"],
                minorFouls=submission["minorFouls"],
                majorFouls=submission["majorFouls"],
                comment=submission["comment"],
                cannedComments=submission["cannedComments"],
                scout=scout
            ):
                abort(400)
        except TypeError as err:
            app.logger.error(f"Error submitting match: {err}")
            abort(400)
    if compLvl == CompLevel.PLAYOFF.value:
        match = setVal
    else:
        match = matchVal

    cannedComments = game.cannedComments

    return render_template(
        "match/submit.html",
        match=match,
        compLvl=compLvl,
        rbtStat=rbtStat,
        teamNum=teamNum,
        setVal=setVal,
        matchVal=matchVal,
        cannedComments=cannedComments,
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

            if not game.scoreRobotInMatch(
                matchNum,
                setNum,
                compLevel,
                station,  # str
                results["startPos"],
                results["preloadFuel"],
                results["autoFuel"],
                results["autoFuelMiss"],
                results["autoClimb"],
                results["firstShift"],
                results["transitionFuel"],
                results["transitionFuelMiss"],
                results["shift1Fuel"],
                results["shift1FuelMiss"],
                results["shift2Fuel"],
                results["shift2FuelMiss"],
                results["shift3Fuel"],
                results["shift3FuelMiss"],
                results["shift4Fuel"],
                results["shift4FuelMiss"],
                results["endgameFuel"],
                results["endgameFuelMiss"],
                EndPositionRebuilt(
                    int(
                        results[ # int between 0-3, though should be 2 or 3 # type: ignore
                            "attemptedEndPos"
                        ]  
                    )
                ),
                results["minorFouls"],
                results["majorFouls"],  # int # type: ignore
                results["comment"],  # str # type: ignore
                results["cannedComments"],  # array of strs # type: ignore
                str(session.get("username")),  # str # type: ignore
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
    curAwesome = (curAwesome + 1) % 3
    return render_template("awesome.html", file="harder" + str(curAwesome + 1) + ".jpg")


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return render_template("auth/logout.html", logoutPageVariable=True)


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
    return render_template("auth/accountManagement.html", users=getAllUsers())


@app.route("/admin")
def adminPage():
    return render_template("auth/admin.html")


@app.route("/strategy/matchTable")
def matchTable():
    matches = getAllMatches()
    results = []
    teams = []
    for match in matches:
        for section in ["red1", "red2", "red3", "blue1", "blue2", "blue3"]:
            if section in match["results"]:
                for result in match["results"][section]:
                    result["team"] = match["teams"][section]
                    result["matchNumber"] = match["matchNumber"]
                    result["setNumber"] = match["setNumber"]
                    result["compLevel"] = match["compLevel"]
                    result["displayName"] = match["displayName"]
                    # cannedComments = result["cannedComments"]
                    # if result["comment"]:
                    #     cannedComments.append(result["comment"])
                    # result["comment"] = ", ".join(cannedComments)
                    results.append(result)
                    if result["team"] not in teams:
                        teams.append(result["team"])

    displayNames = game.matchTableDisplayNames

    return render_template(
        "/strategy/match/table.html",
        results=results,
        displayNames=displayNames,
        teams=teams,
    )


@app.route("/about")
def aboutPage():
    return render_template("about.html")


freeEndpoints = frozenset(
    [
        "login",
        "newUserPage",
        "static",
        "index",
        "logout",
        "aboutPage",
        "awesome",
        "passwordRequestPage",
    ]
)  # endpoints that shouldn't require signing in
adminEndpoints = frozenset(
    [
        "strategyPage",
        "teamRankPage",
        "teamTable",
        "scoreAlliancePage",
        "matchTable",
        "resetPasswordsPage",
        "adminPage",
    ]
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
