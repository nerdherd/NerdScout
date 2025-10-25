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


def addScheduledMatch(
    matchNumber: int,
    setNumber: int,
    compLevel: CompLevel,
    matchKey: str,
    displayName: str,
    red1: int,
    red2: int,
    red3: int,
    blue1: int,
    blue2: int,
    blue3: int,
):
    """
    Adds a single match to the database.
    
    Inputs:
    - matchNumber (int): the match's identification number
    - setNumber (int): the match's set number
    - compLevel (CompLevel): the match's competition level
    - matchKey (str): the match's key, as reported by TBA
    - displayName (str): a human-readable name for the match
    - red1 (int): the number of the team at station red1
    - red2 (int): the number of the team at station red2
    - red3 (int): the number of the team at station red3
    - blue1 (int): the number of the team at station blue1
    - blue2 (int): the number of the team at station blue2
    - blue3 (int): the number of the team at station blue3
    """
    matches.insert_one(
        {
            "matchNumber": matchNumber,
            "setNumber": setNumber,
            "compLevel": compLevel.value,
            "matchKey": matchKey,
            "displayName": displayName,
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
    app.logger.info(  # type: ignore
        f"New match scheduled: Match {compLevel.value}{matchNumber} between red alliance {red1}, {red2}, {red3} and blue alliance {blue1}, {blue2}, {blue3}."
    )


def addMatchFromTBA(match: dict):
    """
    Adds a match using a dict provided by TBA.

    If any error occurs, aborts the request with 500.
    
    Inputs:
    - match (dict): the full dict of a match from TBA
    """
    try:
        compLevel = CompLevel(match["comp_level"])
        matchNumber = match["match_number"]
        setNumber = match["set_number"]
        # TBA uses the same match number for playoffs, only changing set number.
        if compLevel == CompLevel.QUALIFYING:
            displayName = f"Qualifying {matchNumber}"
        elif compLevel == CompLevel.PLAYOFF:
            displayName = f"Playoff {setNumber}"
        elif compLevel == CompLevel.FINAL:
            displayName = f"Final {matchNumber}"
        else:
            displayName = f"{compLevel.value} {matchNumber}"
        addScheduledMatch(
            matchNumber,
            setNumber,
            compLevel,
            match["key"],
            displayName,
            int(match["alliances"]["red"]["team_keys"][0][3:]),
            int(match["alliances"]["red"]["team_keys"][1][3:]),
            int(match["alliances"]["red"]["team_keys"][2][3:]),
            int(match["alliances"]["blue"]["team_keys"][0][3:]),
            int(match["alliances"]["blue"]["team_keys"][1][3:]),
            int(match["alliances"]["blue"]["team_keys"][2][3:]),
        )
    except Exception as e:
        app.logger.error(  # type: ignore
            f"Unable to load match from The Blue Alliance. Aborting. Error: {e}"
        )
        abort(500)


def sortMatches(matches: list):
    """
    Sorts matches by compLevel then matchNumber
    
    Inputs:
    - matches (list[dict]): a list of dicts of matches, as provided by the database
    
    Returns:
    - list[dict]: a list of dicts of matches, sorted
    """
    qualMatches = []
    playoffMatches = []
    finalMatches = []
    otherMatches = []
    for match in matches:
        compLevel = match["compLevel"]
        if compLevel == CompLevel.QUALIFYING.value:
            qualMatches.append(match)
        elif compLevel == CompLevel.PLAYOFF.value:
            playoffMatches.append(match)
        elif compLevel == CompLevel.FINAL.value:
            finalMatches.append(match)
        else:
            otherMatches.append(match)
    if qualMatches:
        qualMatches = sorted(qualMatches, key=lambda match: match["matchNumber"])
    if playoffMatches:
        playoffMatches = sorted(playoffMatches, key=lambda match: match["setNumber"])
    if finalMatches:
        finalMatches = sorted(finalMatches, key=lambda match: match["matchNumber"])
    if otherMatches:
        otherMatches = sorted(otherMatches, key=lambda match: match["matchNumber"])
    return qualMatches + playoffMatches + finalMatches + otherMatches


def sortTeams(teams: list):
    """
    Sorts teams by team number.
    
    Inputs:
    - teams (list[dict]): a list of team dicts, as provided by the database
    
    Returns:
    - list[dict]: a list of team dicts, sorted
    """
    sortedTeams = sorted(teams, key=lambda team: team["number"])
    return sortedTeams


def loadScheduleFromTBA(event: str):
    """
    GETs an event schedule from TBA
    
    Inputs:
    - event (str): event key
    
    Returns:
    - list[dict]: a list of match dicts, as provided by TBA
    """
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/matches/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        if data.status_code == 404:
            abort(400)
        elif not data.ok:
            raise Exception
        data = json.loads(data.text)
    except:
        app.logger.error(f"Failed to load match data for {event} from TBA.")  # type: ignore
        abort(500)
    return data


def addScheduleFromTBA(event: str):
    """
    GETs a schedule from TBA, then adds the matches to the database
    
    Inputs:
    - event (str): event key
    
    Returns:
    - str: "ok" if ok, aborts the request if an error occurs
    """
    if matches.count_documents({}) != 0:
        abort(409)
    data = loadScheduleFromTBA(event)
    for match in data:
        addMatchFromTBA(match)
    return "ok"


def updateScheduleFromTBA(event: str):
    """
    GETs a schedule from TBA, and adds any matches that are not already in the database
    
    Inputs:
    - event (str): event key
    """
    newData = loadScheduleFromTBA(event)
    for match in newData:
        results = matches.count_documents({"matchKey": match["key"]})
        if results == 0:
            addMatchFromTBA(match)


def addTeam(number: int, longName: str, shortName: str, comment: list = []):
    """
    Adds a team to the database
    
    Inputs:
    - number (int): the team's number
    - longName (str): the team's full name, the one with their sponsors, from TBA
    - shortName (str): the team's nickname, or their more common name, from TBA
    - comment (list[str]): any comments for the team
    """
    teams.insert_one(
        {
            "number": number,
            "longName": longName,
            "shortName": shortName,
            "comment": comment,
            "images": [],
        }
    )


def addTeamsFromTBA(event: str):
    """
    GETs the teams for an event and adds them to the database.

    Aborts with 500 if any errors occur
    
    Inputs:
    - event (str): event key
    """
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/teams/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        data = json.loads(data.text)
        if "Error" in data:
            app.logger.error(  # type: ignore
                f"Failed to load team data for {event} from The Blue Alliance. API error: {data['Error']}"
            )
            abort(500)
    except:
        app.logger.error(  # type: ignore
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
            app.logger.error(  # type: ignore
                f"Failed to load team data for {event} from The Blue Alliance. {e}"
            )
            abort(500)


# This always outputs an array, in case there are multiple matches with the same number
def getMatch(compLevel: CompLevel, matchNumber: int, setNumber: int):
    """
    Gets a match from the database
    
    Inputs:
    - compLevel (CompLevel): the match's compLevel
    - matchNumber (int): the match's identification number
    - setNumber (int): the match's set number, usually 1
    
    Returns:
    - list[dict]: a list of match dicts, empty if no matches found
    """
    searchDict = {
        "compLevel": compLevel.value,
        "matchNumber": matchNumber,
        "setNumber": setNumber,
    }
    with matches.find(searchDict) as results:
        parsedResults = parseResults(results)
    return parsedResults


def getAllMatches():
    """
    Gets all matches from the database.
    
    Returns:
    - list[dict]: a list of match dicts, empty if there are no matches
    """
    with matches.find({}) as results:
        parsedResults = parseResults(results)
    return parsedResults


def scoreRobotInMatch(
    matchNumber: int,
    setNumber: int,
    compLevel: CompLevel,
    station: Station,
    startPos: StartingPosition,
    autoLeave: bool,
    autoReef: List[int],
    autoReefMiss: int,
    teleReef: List[int],
    teleReefMiss: int,
    autoProcessor: int,
    autoProcessorMiss: int,
    teleProcessor: int,
    teleProcessorMiss: int,
    autoNet: int,
    autoNetMiss: int,
    teleNet: int,
    teleNetMiss: int,
    endPosSuccess: bool,
    attemptedEndPos: EndPosition,
    minorFouls: int,
    majorFouls: int,
    comment: str,
    cannedComments: List[str],
    scout: str,
):
    """
    Scores one robot in a match.

    Should change every year.

    Inputs:
    - self explanitory
    
    Returns:
    - Boolean: if the robot was successfully scored
    """
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
                    "autoReefMiss": autoReefMiss,
                    "autoReefTotal": autoReef[0] + autoReef[1] + autoReef[2] + autoReef[3],
                    "teleReef": teleReef,
                    "teleReefMiss": teleReefMiss,
                    "teleReefTotal": teleReef[0] + teleReef[1] + teleReef[2] + teleReef[3],
                    "autoProcessor": autoProcessor,
                    "autoProcessorMiss": autoProcessorMiss,
                    "teleProcessor": teleProcessor,
                    "teleProcessorMiss": teleProcessorMiss,
                    "autoNet": autoNet,
                    "autoNetMiss": autoNetMiss,
                    "teleNet": teleNet,
                    "teleNetMiss": teleNetMiss,
                    "endPosSuccess": endPosSuccess,
                    "attemptedEndPos": attemptedEndPos.value,
                    "minorFouls": minorFouls,
                    "majorFouls": majorFouls,
                    "score": calculateScore(
                        autoLeave,
                        autoReef,
                        teleReef,
                        autoProcessor,
                        teleProcessor,
                        autoNet,
                        teleNet,
                        attemptedEndPos.value if endPosSuccess else EndPosition.NONE.value,
                        minorFouls,
                        majorFouls,
                    ),
                    "comment": comment,
                    "cannedComments": cannedComments,
                    "scout": scout,
                }
            }
        },
    )
    if result.matched_count == 0:
        app.logger.info(  # type: ignore
            f"Failed to score robot {station.value} for match {matchNumber} by {scout}: Match does not exist."
        )
        return False
    app.logger.info(f"Robot {station.value} scored for match {matchNumber} by {scout}.")  # type: ignore
    return True


def calculateScoreFromData(matchData: dict, team: Station, edit: int = -1):
    """
    Gets a robot's result from the database and scores it.

    Should change every year.
    
    Inputs:
    - matchData (dict): a match dict
    - team (Station): the station to score
    - edit (int): which revision to score, defaults to the latest
    
    Returns:
    - int: calculated score
    """
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


def addTeamImage(data, team: int, user: str):
    """
    Adds an image a team and store said image in static/teamImages

    Aborts 415 if data is not a png or jpg.
    
    Inputs:
    - data (png or jpg): image to add
    - team (int): the team's number
    - user (str): the username of the uploader
    
    """
    extension = isImage(data)
    if not extension:
        abort(415)
    teamInfo = parseResults(teams.find_one({"number": team}))
    fileLocation = f"teamImages/{team}_{len(teamInfo['images'])}.{extension}"
    open(os.path.join(root, "static/" + fileLocation), "wb").write(data)
    teams.update_one(
        {"number": team},
        {
            "$push": {
                "images": {
                    "location": fileLocation,
                    "scout": user,
                }
            }
        },
    )


def addComment(team: int, comment: str, user: str):
    """
    Adds a comment to a team
    
    Inputs:
    - team (int): the team's number
    - comment (str): the comment to add
    - user (str): the uploader's username
    """
    teams.update_one(
        {"number": team}, {"$push": {"comments": {"comment": comment, "user": user}}}
    )

def pitScoutTeam(team: int, user: str, data:dict):
    """
    Adds a pit scout to a team
    
    Inputs:
    - team (int): the team's number
    - user (str): the uploader's username
    - data (dict): pit scout data
    """
    teams.update_one(
        {"number": team}, {"$push": {"pitScout": {"data": data, "user": user}}}
    )

def getTeam(team: int):
    """
    Gets a team from the database
    
    Inputs:
    - team (int): team number
    
    Returns:
    - dict: the team's dict
    """
    result = teams.find_one({"number": team})
    parsedResults = parseResults(result)
    return parsedResults


def getTeamMatches(team: int):
    """
    Gets all of a team's matches from the database.
        
    Inputs:
    - team (int): team number
    
    Returns:
    - list[dict]: a list of match dicts, from the database
    """
    result = matches.find(
        {
            "$or": [
                {"teams.red1": team},
                {"teams.red2": team},
                {"teams.red3": team},
                {"teams.blue1": team},
                {"teams.blue2": team},
                {"teams.blue3": team},
            ]
        }
    )
    parsedResults = parseResults(result)
    result.close()
    return parsedResults


def getTeamStation(team: int, match: dict):
    """
    Get a team's station from a match dict.
        
    Inputs:
    - team (int): team number
    - match (dict): the match dict, provided by the database
    
    Returns:
    - str or None: the station of the team, or None if the team is not in the match
    """
    station = None
    for key, value in match["teams"].items():
        if value == team:
            station = key
            break
    return station


def getTeamScoredMatches(team: int):
    """
    Gets all of a team's scouted matches.
    
    Inputs:
    - team (int): team number
    
    Returns:
    - list[dict]: list of match dicts, empty if no matches found
    """
    result = getTeamMatches(team)
    filteredResults = []
    for match in result:
        station = getTeamStation(team, match)
        if not station:
            app.logger.error(f'Could not get scored matches for {team}: Failed to get station from match {match["compLevel"]}{match["matchNumber"]} set {match["setNumber"]}.')  # type: ignore
            abort(500)
        if station in match["results"]:
            filteredResults.append(match)
    return filteredResults


# strips out the teams array and all other teams' results
def getTeamResults(team: int):
    """
    Gets a team's results for each of their scored matches.
    
    Inputs:
    - team (int): team number
    
    Returns:
    - list[dict]: list of dicts of the team's match results
    """
    matches = getTeamMatches(team)
    results = []
    for match in matches:
        station = getTeamStation(team, match)
        if not station:
            app.logger.error(f'Could not get results for {team}: Failed to get station from match {match["compLevel"]}{match["matchNumber"]} set {match["setNumber"]}.')  # type: ignore
            abort(500)
        if station in match["results"]:
            resultArray = match["results"][station]
            result = {"results": resultArray}
            result["matchNumber"] = match["matchNumber"]
            result["compLevel"] = match["compLevel"]
            result["setNumber"] = match["setNumber"]
            result["matchKey"] = match["matchKey"]
            result["displayName"] = match["displayName"]
            results.append(result)
    return results


def getAllTeams():
    """
    Gets all teams from the database
    
    Returns:
    - list[dict]: list of team dicts
    """
    with teams.find({}) as results:
        parsedResults = parseResults(results)
    return parsedResults


def getAllUsers():
    """
    Gets all users from the database
    
    Returns:
    - list[dict]: list of account dicts
    """
    return parseResults(accounts.find({}))


def isAdmin(username: str):
    """
    Checks if a user is an admin
    
    Inputs:
    - username (str): the username of the user
    
    Returns:
    - bool: if the provided user is an admin
    """
    return parseResults(accounts.find_one({"username": username}))["admin"]


def getUser(username: str):
    """
    Gets a user from the database
    
    Inputs:
    - username (str): the username of the user
    
    Returns:
    - dict: the user dict of the requested user, empty if not found
    """
    user = accounts.find_one({"username": username})
    return user


def rankTeams(key: str, stat: str, sort: bool = True, reefLevel: int = 0):
    """
    Ranks all teams with match data by a given category.

    Should be edited every year (reefLevel).
    
    Inputs:
    - key (str): the scoring category to rank by
    - stat (str): the statistic to rank using, either "mean", "median", "mode", "highest", or "lowest"
    - sort (bool): True for descending, False for ascending, defaults to true.
    - reefLevel (int): if the data is a list, such as reef data, which index to use
    
    Returns:
    - list[dict]: the ranked teams with their calculated statistic
    """
    teams = sortTeams(getAllTeams())
    calculate = (
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
                    else getMatchWithLowestValue if stat == "lowest" else None
                )
            )
        )
    )
    if not calculate:
        return None
    for team in teams:
        team[key] = calculate(getTeamResults(team["number"]), key, reefLevel)
    isDict = stat == "highest" or stat == "lowest"
    if isDict:
        return sorted(teams, key=lambda team: team[key]["value"], reverse=sort)
    else:
        return sorted(teams, key=lambda team: team[key], reverse=sort)


def calculateAverageAllianceScore(team1: int, team2: int, team3: int, calc=getMeanOfScoringCategory):
    """
    Calculates a hypothetical alliance score of three teams using their average results in each category.

    Should be edited every year.
    
    Inputs:
    - team1 (int): team number 1
    - team2 (int): team number 2
    - team3 (int): team number 3
    - calc (function): the static function to use, defaults to mean
    
    Returns:
    - dict or none: dict of predicted results, or None if any teams are not found.
    """
    team1Listing = getTeam(team1)
    if not team1Listing:
        return None
    team2Listing = getTeam(team2)
    if not team2Listing:
        return None
    team3Listing = getTeam(team3)
    if not team3Listing:
        return None

    team1Data = getTeamResults(team1)
    team2Data = getTeamResults(team2)
    team3Data = getTeamResults(team3)

    team1Leave = int(calc(team1Data, "autoLeave") >= 0.5)
    team2Leave = int(calc(team2Data, "autoLeave") >= 0.5)
    team3Leave = int(calc(team3Data, "autoLeave") >= 0.5)
    leaveTotal = team1Leave + team2Leave + team3Leave

    team1End = round(calc(team1Data, "endPos"))
    team2End = round(calc(team2Data, "endPos"))
    team3End = round(calc(team3Data, "endPos"))

    team1Minors = calc(team1Data, "minorFouls")
    team2Minors = calc(team2Data, "minorFouls")
    team3Minors = calc(team3Data, "minorFouls")

    team1Majors = calc(team1Data, "majorFouls")
    team2Majors = calc(team2Data, "majorFouls")
    team3Majors = calc(team3Data, "majorFouls")

    autoReef = [
        round(calc(team1Data, "autoReef", 0))
        + round(calc(team2Data, "autoReef", 0))
        + round(calc(team3Data, "autoReef", 0)),
        round(calc(team1Data, "autoReef", 1))
        + round(calc(team2Data, "autoReef", 1))
        + round(calc(team3Data, "autoReef", 1)),
        round(calc(team1Data, "autoReef", 2))
        + round(calc(team2Data, "autoReef", 2))
        + round(calc(team3Data, "autoReef", 2)),
        round(calc(team1Data, "autoReef", 3))
        + round(calc(team2Data, "autoReef", 3))
        + round(calc(team3Data, "autoReef", 3)),
    ]

    autoReef[0] += (max(autoReef[1],12)-12) + (max(autoReef[2],12)-12) + (max(autoReef[3],12)-12)
    
    autoReef = [
        autoReef[0],
        min(autoReef[1],12),
        min(autoReef[2],12),
        min(autoReef[3],12),
    ]

    teleReefValues = [
        round(calc(team1Data, "teleReef", 0))
        + round(calc(team2Data, "teleReef", 0))
        + round(calc(team3Data, "teleReef", 0)),
        round(calc(team1Data, "teleReef", 1))
        + round(calc(team2Data, "teleReef", 1))
        + round(calc(team3Data, "teleReef", 1)),
        round(calc(team1Data, "teleReef", 2))
        + round(calc(team2Data, "teleReef", 2))
        + round(calc(team3Data, "teleReef", 2)),
        round(calc(team1Data, "teleReef", 3))
        + round(calc(team2Data, "teleReef", 3))
        + round(calc(team3Data, "teleReef", 3)),
    ]
    
    teleReef = [
        teleReefValues[0],
        min(teleReefValues[1],12-autoReef[1]),
        min(teleReefValues[1],12-autoReef[1]),
        min(teleReefValues[1],12-autoReef[1])
    ]
    teleReef[0] += max(0,teleReefValues[1]-teleReef[1]) + max(0,teleReefValues[2]-teleReef[2]) + max(0,teleReefValues[3]-teleReef[3])

    autoProcessor = (
        round(calc(team1Data, "autoProcessor"))
        + round(calc(team2Data, "autoProcessor"))
        + round(calc(team3Data, "autoProcessor"))
    )
    teleProcessor = (
        round(calc(team1Data, "teleProcessor"))
        + round(calc(team2Data, "teleProcessor"))
        + round(calc(team3Data, "teleProcessor"))
    )

    autoNet = (
        round(calc(team1Data, "autoNet"))
        + round(calc(team2Data, "autoNet"))
        + round(calc(team3Data, "autoNet"))
    )
    teleNet = (
        round(calc(team1Data, "teleNet"))
        + round(calc(team2Data, "teleNet"))
        + round(calc(team3Data, "teleNet"))
    )

    score = calculateScore(
        False,
        autoReef,
        teleReef,
        autoProcessor,
        teleProcessor,
        autoNet,
        teleNet,
        0,
        0,
        0,
    )

    score += 3 * leaveTotal
    score += (
        2
        if team1End == EndPosition.PARK.value
        else (
            6
            if team1End == EndPosition.SHALLOW.value
            else 12 if team1End == EndPosition.DEEP.value else 0
        )
    )
    score += (
        2
        if team2End == EndPosition.PARK.value
        else (
            6
            if team2End == EndPosition.SHALLOW.value
            else 12 if team2End == EndPosition.DEEP.value else 0
        )
    )
    score += (
        2
        if team3End == EndPosition.PARK.value
        else (
            6
            if team3End == EndPosition.SHALLOW.value
            else 12 if team3End == EndPosition.DEEP.value else 0
        )
    )

    return {
        "score": score,
        "autoLeave": leaveTotal,
        "autoReef": autoReef,
        "teleReef": teleReef,
        "autoProcessor": autoProcessor,
        "teleProcessor": teleProcessor,
        "autoNet": autoNet,
        "teleNet": teleNet,
        "endPos1": team1End,
        "endPos2": team2End,
        "endPos3": team3End,
        "minorFouls": team1Minors + team2Minors + team3Minors,
        "majorFouls": team1Majors + team2Majors + team3Majors,
    }


def calculateMinMaxAllianceScore(
    team1: int, team2: int, team3: int, maximum: bool = True
):
    """
    Calculates a hypothetical alliance score of three teams using their minimum or maximum results in each category.

    Should be edited every year.
    
    Inputs:
    - team1 (int): team number 1
    - team2 (int): team number 2
    - team3 (int): team number 3
    - maximum (bool): True uses maximum, False uses minimum, defaults to True
    
    Returns:
    - dict or none: dict of predicted results, or None if any teams are not found.
    """
    statistic = getMatchWithHighestValue if maximum else getMatchWithLowestValue
    oppositeStatistic = getMatchWithLowestValue if maximum else getMatchWithHighestValue

    team1Listing = getTeam(team1)
    if not team1Listing:
        return None
    team2Listing = getTeam(team2)
    if not team2Listing:
        return None
    team3Listing = getTeam(team3)
    if not team3Listing:
        return None

    team1Data = getTeamResults(team1)
    team2Data = getTeamResults(team2)
    team3Data = getTeamResults(team3)

    team1Leave = statistic(team1Data, "autoLeave")["value"]
    team2Leave = statistic(team2Data, "autoLeave")["value"]
    team3Leave = statistic(team3Data, "autoLeave")["value"]
    leaveTotal = team1Leave + team2Leave + team3Leave

    team1End = statistic(team1Data, "endPos")["value"]
    team2End = statistic(team2Data, "endPos")["value"]
    team3End = statistic(team3Data, "endPos")["value"]

    team1Minors = statistic(team1Data, "minorFouls")["value"]
    team2Minors = statistic(team2Data, "minorFouls")["value"]
    team3Minors = statistic(team3Data, "minorFouls")["value"]

    team1Majors = statistic(team1Data, "majorFouls")["value"]
    team2Majors = statistic(team2Data, "majorFouls")["value"]
    team3Majors = statistic(team3Data, "majorFouls")["value"]

    autoReef = [
        round(statistic(team1Data, "autoReef", 0)["value"])
        + round(statistic(team2Data, "autoReef", 0)["value"])
        + round(statistic(team3Data, "autoReef", 0)["value"]),
        round(statistic(team1Data, "autoReef", 1)["value"])
        + round(statistic(team2Data, "autoReef", 1)["value"])
        + round(statistic(team3Data, "autoReef", 1)["value"]),
        round(statistic(team1Data, "autoReef", 2)["value"])
        + round(statistic(team2Data, "autoReef", 2)["value"])
        + round(statistic(team3Data, "autoReef", 2)["value"]),
        round(statistic(team1Data, "autoReef", 3)["value"])
        + round(statistic(team2Data, "autoReef", 3)["value"])
        + round(statistic(team3Data, "autoReef", 3)["value"]),
    ]

    autoReef[0] += (max(autoReef[1],12)-12) + (max(autoReef[2],12)-12) + (max(autoReef[3],12)-12)
    
    autoReef = [
        autoReef[0],
        min(autoReef[1],12),
        min(autoReef[2],12),
        min(autoReef[3],12),
    ]

    teleReefValues = [
        round(statistic(team1Data, "teleReef", 0)["value"])
        + round(statistic(team2Data, "teleReef", 0)["value"])
        + round(statistic(team3Data, "teleReef", 0)["value"]),
        round(statistic(team1Data, "teleReef", 1)["value"])
        + round(statistic(team2Data, "teleReef", 1)["value"])
        + round(statistic(team3Data, "teleReef", 1)["value"]),
        round(statistic(team1Data, "teleReef", 2)["value"])
        + round(statistic(team2Data, "teleReef", 2)["value"])
        + round(statistic(team3Data, "teleReef", 2)["value"]),
        round(statistic(team1Data, "teleReef", 3)["value"])
        + round(statistic(team2Data, "teleReef", 3)["value"])
        + round(statistic(team3Data, "teleReef", 3)["value"]),
    ]
    
    teleReef = [
        teleReefValues[0],
        min(teleReefValues[1],12-autoReef[1]),
        min(teleReefValues[1],12-autoReef[1]),
        min(teleReefValues[1],12-autoReef[1])
    ]
    teleReef[0] += max(0,teleReefValues[1]-teleReef[1]) + max(0,teleReefValues[2]-teleReef[2]) + max(0,teleReefValues[3]-teleReef[3])

    autoProcessor = (
        statistic(team1Data, "autoProcessor")["value"]
        + statistic(team2Data, "autoProcessor")["value"]
        + statistic(team3Data, "autoProcessor")["value"]
    )
    teleProcessor = (
        statistic(team1Data, "teleProcessor")["value"]
        + statistic(team2Data, "teleProcessor")["value"]
        + statistic(team3Data, "teleProcessor")["value"]
    )

    autoNet = (
        statistic(team1Data, "autoNet")["value"]
        + statistic(team2Data, "autoNet")["value"]
        + statistic(team3Data, "autoNet")["value"]
    )
    teleNet = (
        statistic(team1Data, "teleNet")["value"]
        + statistic(team2Data, "teleNet")["value"]
        + statistic(team3Data, "teleNet")["value"]
    )

    score = calculateScore(
        False,
        autoReef,
        teleReef,
        autoProcessor,
        teleProcessor,
        autoNet,
        teleNet,
        0,
        0,
        0,
    )

    score += 3 * leaveTotal
    score += (
        2
        if team1End == EndPosition.PARK.value
        else (
            6
            if team1End == EndPosition.SHALLOW.value
            else 12 if team1End == EndPosition.DEEP.value else 0
        )
    )
    score += (
        2
        if team2End == EndPosition.PARK.value
        else (
            6
            if team2End == EndPosition.SHALLOW.value
            else 12 if team2End == EndPosition.DEEP.value else 0
        )
    )
    score += (
        2
        if team3End == EndPosition.PARK.value
        else (
            6
            if team3End == EndPosition.SHALLOW.value
            else 12 if team3End == EndPosition.DEEP.value else 0
        )
    )

    return {
        "score": score,
        "autoLeave": leaveTotal,
        "autoReef": autoReef,
        "teleReef": teleReef,
        "autoProcessor": autoProcessor,
        "teleProcessor": teleProcessor,
        "autoNet": autoNet,
        "teleNet": teleNet,
        "endPos1": team1End,
        "endPos2": team2End,
        "endPos3": team3End,
        "minorFouls": team1Minors + team2Minors + team3Minors,
        "majorFouls": team1Majors + team2Majors + team3Majors,
    }


# converts database results to JSON
# the default functions get stuck on ObjectID objects
def parseResults(data):
    """
    Parses results from the database.
    
    Inputs:
    - data (Cursor): raw output from the database
    
    Returns:
    - dict or list: parsed results
    """
    return json.loads(json_util.dumps(data))
