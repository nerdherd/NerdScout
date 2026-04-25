import os
from flask import (
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_squeeze import Squeeze
from minify_html import minify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash
import random
import time
from constants import *
from database import *
from auth import *
from games import *

squeeze = Squeeze()

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config["JSON_SORT_KEYS"] = False

app.config.from_mapping(
    SECRET_KEY=open(os.path.join(root, "secrets/secretKey"), "r").read()
)

app.jinja_env.filters["any"] = any

game = Rebuilt(matches, teams)

squeeze.init_app(app)

generatePoints()


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
    if not app.debug:
        app.logger.error("Request recieved to create test matches, but server not in debug mode.")
        abort(404)
    foundationNames = (
        "Abaca",
        "Louis & Lewis",
        "Super Evil Wevils",
        "Wheler",
        "Mr. Hello's",
        "John",
    )
    for i, foundationName in zip(range(9991, 9997), foundationNames):
        if not getTeam(i):
            addTeam(i, f"{foundationName} Foundation", foundationName)
    for i in range(9991, 9996):
        if not getMatch(CompLevel.QM, i, 1):
            addScheduledMatch(
                i,
                1,
                CompLevel.QM,
                f"2026test_qm{i}",
                f"TestMatch {i}",
                9991,
                9992,
                9993,
                9994,
                9995,
                9996,
            )
            addTestTBAData(CompLevel.QM,i,1)
            addTestPredictionToDatabase(f"2026test_qm{i}")
    coinflip = lambda: random.random() > 0.5
    for i in range(9991, 9996):
        for team in Station:
            feeding = (coinflip())
            defending = (coinflip())
            game.scoreRobotInMatch(
                matchNumber=i,
                setNumber=1,
                compLevel=CompLevel.QM,
                station=team,
                startPos=random.randint(0,2),
                preloadFuel=random.randint(0, 8),
                autoFuelTotal=random.randint(0,100),
                autoDepot=coinflip(),
                autoBump=coinflip(),
                autoTrench=coinflip(),
                autoNeutralIntake=coinflip(),
                autoAttemptedSecondScore=coinflip(),
                autoSucceededSecondScore=coinflip(),
                autoClimbAttempted=coinflip(),
                autoClimbSuccess=coinflip(),
                autoOutpostFeed=coinflip(),
                autoFedToOutpost=coinflip(),
                firstShift=coinflip(),
                transitionFuelTotal=random.randint(0,100),
                transitionFed=coinflip(),
                transitionDefense=coinflip(),
                transitionStole=coinflip(),
                firstActiveShiftFuelTotal=random.randint(0,100),
                firstActiveShiftFed=coinflip(),
                firstActiveShiftDefense=coinflip(),
                firstActiveShiftStole=coinflip(),
                secondActiveShiftFuelTotal=random.randint(0,100),
                secondActiveShiftFed=coinflip(),
                secondActiveShiftDefense=coinflip(),
                secondActiveShiftStole=coinflip(),
                firstInactiveShiftScored=coinflip(),
                firstInactiveShiftFed=coinflip(),
                firstInactiveShiftDefense=coinflip(),
                firstInactiveShiftStole=coinflip(),
                firstInactiveShiftIntaked=coinflip(),
                secondInactiveShiftScored=coinflip(),
                secondInactiveShiftFed=coinflip(),
                secondInactiveShiftDefense=coinflip(),
                secondInactiveShiftStole=coinflip(),
                secondInactiveShiftIntaked=coinflip(),
                endgameFuelTotal=random.randint(0,100),
                endgameFed=coinflip(),
                endgameDefense=coinflip(),
                endgameStole=coinflip(),
                endClimb=EndPositionRebuilt(random.randint(0, 3)),
                endClimbAttempted=EndPositionRebuilt(random.randint(0, 3)),
                outpostIntake=coinflip(),
                groundIntake=coinflip(),
                fedToOutpost=coinflip(),
                feedingRank=random.randint(1,10) if feeding else None,
                feedingComment="this robot was feeding :3" if feeding else None,
                defenseRank=random.randint(1,10) if defending else None,
                defenseComment="this robot was defending >:(" if defending else None,
                stealRank=random.randint(1,10) if coinflip() else None,
                driverRank=random.randint(1,10),
                vibeCheck=random.randint(1,10),
                minorFouls=random.randint(0, 10),
                majorFouls=random.randint(0, 3),
                comment="abaca",
                cannedComments=[],
                scout=random.choice(
                    [
                        "hello",
                        "hello2",
                        "hlelo3",
                        "tonnieboy300",
                        "mr hello",
                        "hello jr",
                        "ms hello",
                    ]
                ),
            )
    writeToCacheFile("2026test", "recentEventKey")
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

    nextMatch = None
    nextMatch = getMatch(compLevel, matchNumber + 1, setNumber)
    if not nextMatch:
        nextMatch = getMatch(compLevel, matchNumber, setNumber + 1)

    # under normal conditions, SF matches shouldn't exist unless qualification is done.
    if not nextMatch and compLevel == CompLevel.QM:
        nextMatch = getMatch(CompLevel.SF,1,1)

    # standard 8-alliance brackets have 13 playoffs before finals
    if compLevel == CompLevel.SF and setNumber == 13:
        nextMatch = getMatch(CompLevel.F,1,1)

    if nextMatch:
        nextMatch = nextMatch[-1]

    showAdmin = session["username"] and isDbAdmin(session["username"])

    alert = ""
    if "alert" in request.args:
        alert = request.args.get("alert")

    madePrediction = False
    if session["username"]:
        userData = getUser(session["username"])
        if userData:
            if "predictions" in userData:
                madePrediction = results["matchKey"] in userData["predictions"]
            userPoints = userData["points"]

    return render_template(
        "match/match.html",
        teams=[redTeams, blueTeams],
        matchData=matchData,
        results=results,
        nextMatch=nextMatch,
        showAdmin=showAdmin,
        alert=alert,
        matchNum=matchNumber,
        compLevel=compLevel.value,
        setNum=setNumber,
        madePrediction=madePrediction,
        userPoints=userPoints,
        # this is game specific.
        FMSEndPositionRebuilt=FMSEndPositionRebuilt,
    )


@app.route("/match/nerdPredictSubmitScore", methods=["POST"])
def createPredictionPage():
    if request.method == "POST":
        print("posted")
        submission = request.json
        try:
            compLevel = CompLevel(submission["compLevel"])
            matchNumber = int(submission["matchNumber"])
            setNumber = int(submission["setNumber"])
            forRed = bool(submission["forRed"])
            difference = float(submission["difference"])
            statsForRed = bool(submission["statsForRed"])
            points = int(submission["points"])
        except TypeError as e:
            print(e)
            abort(400)
        createPrediction(
            session["username"],
            compLevel,
            matchNumber,
            setNumber=setNumber,
            forRed=forRed,
            difference=difference,
            statsForRed=statsForRed,
            points=points,
        )
        return "ok"
    abort(405)


@app.route("/match/updateFromTBA")
def updateMatchFromTBAPage():
    try:
        matchNumber = int(request.args.get("matchNum"))  # type: ignore
        compLevel = CompLevel(request.args.get("compLevel"))  # type: ignore
        setNumber = int(request.args.get("setNum"))  # type: ignore
    except:
        abort(400)
    # success = addTestTBAData(compLevel=compLevel,matchNumber=matchNumber,setNumber=setNumber)
    result = updateMatchFromTBA(
        compLevel=compLevel, matchNumber=matchNumber, setNumber=setNumber
    )
    if result[0]:
        updateAllStatboticsPredictions()
        saveAlliancesFromTBA()
    if compLevel == CompLevel.SF or compLevel == CompLevel.F:
        updateScheduleFromTBA(loadFromCacheFile("recentEventKey"))
    return redirect(
        url_for(
            "renderMatch",
            matchNum=matchNumber,
            compLevel=compLevel.value,
            setNum=setNumber,
            alert="Successfully updated match!" if result[0] else f"Failed to update match. {result[1]}",
        )
    )


@app.route("/team")
def teamPage():
    app.logger.info(f"Loading Team Page: {time.time()}")
    try:
        team = int(request.args.get("team"))  # type: ignore
        results = getTeam(team)
    except TypeError as err:
        statMatrices = game.calculateStatMatrices()
        return render_template(
            "team/teamSelect.html", teams=sortTeams(getAllTeams()), team=-1, statMatrices=statMatrices
        )

    if results is None:
        statMatrices = game.calculateStatMatrices()
        return render_template(
            "team/teamSelect.html", teams=sortTeams(getAllTeams()), team=team, statMatrices=statMatrices
        )

    matches = getTeamMatches(team)
    stats = game.getAllStats(team)
    statMatrix = game.calculateStatMatrix(team,game.getMaximumsForStatMatrix())
    return render_template(
        "team/team.html",
        team=results,
        matches=sortMatches(matches),
        stats=stats,
        keyDisplayNames=game.keyDisplayNames,
        pitScoutQuestions=game.pitScout,
        statMatrix=statMatrix
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
    eventKey = loadFromCacheFile("recentEventKey")
    return render_template("match/schedule/addSchedule.html", eventKey=eventKey)


@app.route("/updateSchedule", methods=["GET", "POST"])
def updateSchedulePage():
    if request.method == "POST":
        try:
            data = request.json
            event = str(data["code"])  # type: ignore
        except:
            abort(400)
        updateScheduleFromTBA(event)
    eventKey = loadFromCacheFile("recentEventKey")
    return render_template("match/schedule/updateSchedule.html", eventKey=eventKey)


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
    return render_template(
        "team/pitScout.html",
        team=team,
        pitScout = game.pitScout
    )

@app.route("/team/csv")
def getPitScoutCSV():
    
    csv = ["team","user"]
    for section in game.pitScout:
        for question in section:
            if question["type"] == "text":
                csv.append(question["text"])
            elif question["type"] == "select":
                # csv.append(question["id"]+"select")
                for option in question["options"]:
                    csv.append(question["text"]+" - "+option[0])
    csv = [csv]

    teams = getAllTeams()
    for team in teams:
        if "pitScout" in team:
            scouted = team["pitScout"][-1]
            line = [team['number'],scouted['user']]
            scouted = scouted["data"]
            for section in game.pitScout:
                for question in section:
                    if question["type"] == "text":
                        # csv.append(question["id"])
                        line.append(scouted[question["id"]])
                    elif question["type"] == "select":
                        # csv.append(question["id"]+"select")
                        for option in question["options"]:
                            line.append(scouted[question["id"]][option[1]])
            csv.append(line)
    
    csv = [[str(a) for a in row] for row in csv]
    csv = [[a.replace("\"","\\\"\\\"") for a in row] for row in csv]
    csv = [["\\\""+a+"\\\"" for a in row] for row in csv]
    csv = "\\n".join(",".join(row) for row in csv)

    return render_template("team/downloadCSV.html",csvdata=csv)


# dontSummarize = frozenset(
#     [
#         "startPos",
#         "endPos",
#         "attemptedEndPos",
#         "cannedComments",
#         "endPosSuccess",
#         "autoFuel",
#         "transitionFuel",
#         "firstActiveShiftFuel",
#         "secondActiveShiftFuel",
#         "endgameFuel",
#     ]
# )

possibleTeamTableKeys = frozenset(game.teamTableDisplayNames.keys())


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
        data.append({"team": team["number"], "results": {}})
        results = getTeamResults(team["number"])
        if not results:
            continue
        for key, result in results[0]["results"][0].items():
            if (type(result) == str) or not (key in possibleTeamTableKeys):
                continue
            # if type(result) == list:
            #     i = 0
            #     for level in result:
            #         piece = method(results, key, i)
            #         if isAnObject:
            #             data[-1]["results"].append({f"{key}L{i+1}": piece["value"], "matchId": f"{matchViewer}?matchNum={piece['matchNumber']}&compLevel={piece['compLevel']}&setNum={piece['setNumber']}"})  # type: ignore
            #         else:
            #             data[-1]["results"].append({f"{key}L{i+1}": piece})
            #         i += 1
            else:
                piece = method(results, key)
                data[-1]["results"][key] = {}
                if isAnObject:
                    data[-1]["results"][key]["value"] = piece["value"] # type: ignore
                    data[-1]["results"][key]["matchId"] = f"{matchViewer}?matchNum={piece['matchNumber']}&compLevel={piece['compLevel']}&setNum={piece['setNumber']}"  # type: ignore
                else:
                    data[-1]["results"][key]["value"] = piece

    return data


@app.route("/strategy/teamtable")
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
    links = stat == "highest" or stat == "lowest"

    displayNames = game.teamTableDisplayNames
    data = teamDataSummary()
    print([a for a in data[-1]["results"].keys()])
    print(data)
    return render_template(
        "strategy/team/table.html",
        displayNames=displayNames,
        data=data,
        links=links,
        stat=stat,
    )


@app.route("/nerdpredict/leaderboard")
def pointsLeaderboardPage():
    ranking = getPointsRankings()
    return render_template("predict/rank.html", ranking=ranking)


@app.route("/nerdpredict/playoffs", methods=["GET", "POST"])
def pointsPlayoffsPage():
    userData = getUser(session["username"])
    if userData and "points" in userData:
        userPoints = userData["points"]
    else:
        userPoints = 0
    if request.method == "POST":
        rawData = request.json
        if (not rawData) or ("redwon" not in rawData):
            abort(400)
        redwon = [a == "true" for a in rawData["redwon"].split(",")]
        if len(redwon) != 14:
            abort(400)
        if not ("points" in rawData):
            abort(400)
        try:
            points = int(rawData["points"])
        except ValueError:
            abort(400)
        username = str(session.get("username"))
        if not createPickEms(
            username,
            points,
            redwon[0],
            redwon[1],
            redwon[2],
            redwon[3],
            redwon[4],
            redwon[5],
            redwon[6],
            redwon[7],
            redwon[8],
            redwon[9],
            redwon[10],
            redwon[11],
            redwon[12],
            redwon[13],
        ):
            abort(500)
        else:
            return "yay!! yippee!"
    try:
        allianceData = json.loads(loadFromCacheFile("alliances"))
        if (allianceData["eventKey"] != loadFromCacheFile("recentEventKey")) and ("Archimedes" not in allianceData):
            allianceData = None
    except:
        allianceData = None
    alliances = []
    einsteinNames = [
        "Archimedes",
        "Curie",
        "Daly",
        "Galileo",
        "Hopper",
        "Johnson",
        "Milstein",
        "Newton"
    ]
    worlds = False
    if (allianceData != None) and (allianceData["rawData"] != None):
        try:
            if "Archimedes" in allianceData:
                for i in range(len(einsteinNames)):
                    alliance = allianceData[einsteinNames[i]]
                    if len(alliance) > 4:
                        alliance = alliance[:4]
                    alliances.append(alliance)
                worlds = True
            else:
                for i in range(1,9):
                    alliance = allianceData[f"Alliance {i}"]
                    # sometimes an alliance has four members
                    # this will be bad at worlds, where four members is standard
                    if len(alliance) > 3:
                        alliance = alliance[:3]
                    alliances.append(alliance)
        except:
            alliances = []
    
    playoff1 = getMatch(CompLevel.SF,1,1)
    if playoff1:
        playoff1 = playoff1[-1]
    return render_template(
        "predict/playoffs.html",
        isAdmin=isDbAdmin(session['username']),
        alliances=alliances,
        userPoints=userPoints,
        userData=userData,
        playoff1=playoff1,
        worlds=worlds
    )

@app.route("/nerdpredict/playoffs/pay", methods=["POST"])
def finishPlayoffsPage():
    status = payPickEms()
    if status:
        return "good"
    else:
        return "bad", 400
    
@app.route("/nerdpredict/playoffs/loadWorldsAlliances")
def getWorldsAlliancesPage():
    # TODO: Change for the current season's worlds.
    saveAlliancesFromTBA("2026cmptx")
    return "make sure to clear out the match database and pull the matches for einstein and also remove all the pickems"


@app.route("/nerdpredict")
def nerdpredictMain():
    return render_template("predict/index.html")


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
                autoFuelTotal=submission["autoFuelTotal"],
                autoDepot=submission["autoDepot"],
                autoBump=submission["autoBump"],
                autoTrench=submission["autoTrench"],
                autoNeutralIntake=submission["autoNeutralIntake"],
                autoAttemptedSecondScore=submission["autoAttemptedSecondScore"],
                autoSucceededSecondScore=submission["autoSucceededSecondScore"],
                autoClimbAttempted=submission["autoClimbAttempted"],
                autoClimbSuccess=submission["autoClimbSuccess"],
                autoOutpostFeed=submission["autoOutpostFeed"],
                autoFedToOutpost=submission["autoFedToOutpost"],
                firstShift=submission["firstShift"],
                transitionFuelTotal=submission["transitionFuelTotal"],
                transitionFed=submission["transitionFed"],
                transitionDefense=submission["transitionDefense"],
                transitionStole=submission["transitionStole"],
                firstActiveShiftFuelTotal=submission["firstActiveShiftFuelTotal"],
                firstActiveShiftFed=submission["firstActiveShiftFed"],
                firstActiveShiftDefense=submission["firstActiveShiftDefense"],
                firstActiveShiftStole=submission["firstActiveShiftStole"],
                secondActiveShiftFuelTotal=submission["secondActiveShiftFuelTotal"],
                secondActiveShiftFed=submission["secondActiveShiftFed"],
                secondActiveShiftDefense=submission["secondActiveShiftDefense"],
                secondActiveShiftStole=submission["secondActiveShiftStole"],
                firstInactiveShiftScored=submission["firstInactiveShiftScored"],
                firstInactiveShiftFed=submission["firstInactiveShiftFed"],
                firstInactiveShiftDefense=submission["firstInactiveShiftDefense"],
                firstInactiveShiftStole=submission["firstInactiveShiftStole"],
                firstInactiveShiftIntaked=submission["firstInactiveShiftIntaked"],
                secondInactiveShiftScored=submission["secondInactiveShiftScored"],
                secondInactiveShiftFed=submission["secondInactiveShiftFed"],
                secondInactiveShiftDefense=submission["secondInactiveShiftDefense"],
                secondInactiveShiftStole=submission["secondInactiveShiftStole"],
                secondInactiveShiftIntaked=submission["secondInactiveShiftIntaked"],
                endgameFuelTotal=submission["endgameFuelTotal"],
                endgameFed=submission["endgameFed"],
                endgameDefense=submission["endgameDefense"],
                endgameStole=submission["endgameStole"],
                endClimb=EndPositionRebuilt(
                    int(
                        submission[  # int between 0-3, though should be 2 or 3 # type: ignore
                            "endClimb"
                        ]
                    )
                ),
                endClimbAttempted=EndPositionRebuilt(
                    int(
                        submission[  # int between 0-3, though should be 2 or 3 # type: ignore
                            "endClimbAttempted"
                        ]
                    )
                ),
                outpostIntake=submission["outpostIntake"],
                groundIntake=submission["groundIntake"],
                fedToOutpost=submission["fedToOutpost"],
                feedingRank=submission["feedingRank"],
                feedingComment=submission["feedingComment"],
                defenseRank=submission["defenseRank"],
                defenseComment=submission["defenseComment"],
                stealRank=submission["stealRank"],
                driverRank=submission["driverRank"],
                vibeCheck=submission["vibeCheck"],
                minorFouls=submission["minorFouls"],
                majorFouls=submission["majorFouls"],
                comment=submission["comment"],
                cannedComments=submission["cannedComments"],
                scout=scout,
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
    return "not implemented"
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
                        results[  # int between 0-3, though should be 2 or 3 # type: ignore
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
    # return "not implemented"
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

@app.route("/clearAllPickems")
def clearPickemsPage():
    clearPickems()
    return "yeag"


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
        "getPitScoutCSV"
    ]
)  # endpoints that require user be admin

dbAdminEndpoints = frozenset(
    [
        "updateMatchFromTBAPage",
        "finishPlayoffsPage",
        "clearPickemsPage",
        "getWorldsAlliancesPage",
    ]
)  # endpoints that require user be dbAdmin


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

    if request.endpoint in dbAdminEndpoints and not isDbAdmin(session["username"]):
        app.logger.warning(
            f"User {session['username']} attempted to access {request.endpoint} without dbAdmin"
        )
        abort(403)

@app.after_request
def after_request(response):
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )
        return response
    return response


@app.errorhandler(HTTPException)
def pageNotFound(e):
    response = e.get_response()
    return render_template("error.html", code=e.code, name=e.name), e.code


if __name__ == "__main__":
    app.run(debug=True)
