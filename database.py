from array import array
from datetime import datetime
from http.client import HTTPException
import os
import re
from time import time, time_ns
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
requestsDB = database.requests


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
            f"https://www.thebluealliance.com/api/v3/event/{event}/matches",
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
        else:
            if "score_breakdown" in match:
                matches.update_one({"matchKey": match["key"]},{"$set":{"results.scored":True}})
                matchInDB = parseResults(matches.find_one({"matchKey": match["key"]}))
                if (not "scoreBreakdown" in matchInDB["results"]) or (matchInDB["results"]["scoreBreakdown"]["postResultTime"] < match["post_result_time"]):
                    matches.update_one({"matchKey": match["key"]},{"$set":{"results.postResultTime": match["post_result_time"], "results.actualTime": match["actual_time"], "results.scoreBreakdown": match["score_breakdown"], "results.winningAlliance": match["winning_alliance"]}})


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


def pitScoutTeam(team: int, user: str, data: dict):
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


def rankTeams(key: str, stat: str, sort: bool = True, index: int = 0):
    """
    Ranks all teams with match data by a given category.

    Inputs:
    - key (str): the scoring category to rank by
    - stat (str): the statistic to rank using, either "mean", "median", "mode", "highest", or "lowest"
    - sort (bool): True for descending, False for ascending, defaults to true.
    - index (int): if the data is a list, which index to use

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
        team[key] = calculate(getTeamResults(team["number"]), key, index)
    isDict = stat == "highest" or stat == "lowest"
    if isDict:
        return sorted(teams, key=lambda team: team[key]["value"], reverse=sort)
    else:
        return sorted(teams, key=lambda team: team[key], reverse=sort)


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

def generatePoints() -> bool:
    """
    Gives accounts a points field if they do not yet.

    Returns:
    - bool: succeeded
    """
    return accounts.update_many({"points": {"$exists":False}},{"$set":{"points": 0}}).acknowledged

def changeAccountPoints(username:str, pointsChange: int) -> bool:
    """
    Increments a user's points

    Inputs:
    - username (str): username of user
    - pointsChange (int): points to add or subtract

    Returns:
    - bool: succeeded
    """
    return accounts.update_many({"username": username},{"$inc":{"points":pointsChange}}).acknowledged

def changeAllAccountPoints(pointsChange: int) -> bool:
    """
    Increments all user's points

    Inputs:
    - pointsChange (int): points to add or subtract

    Returns:
    - bool: succeeded
    """
    return accounts.update_many({},{"$inc":{"points":pointsChange}}).acknowledged

def getPointsRankings() -> list[dict]:
    """
    Returns a leaderboard for points.

    Returns:
    - list[dict]: leaderboard
    """
    users = getAllUsers()
    nonapproved = []
    # remove sensitive data
    for i in range(len(users)):
        if not users[i]["approved"]:
            nonapproved.append(i)
        users[i].pop("passwordHash")
        users[i].pop("approved")
        users[i].pop("admin")
    for user in nonapproved:
        users.pop(user)
    return sorted(users,key=lambda user: user["points"],reverse=True)

def createPrediction(user: str, compLevel: CompLevel, matchNumber: int, setNumber: int, forRed: bool, points: int) -> None:
    """
    Create a new prediction for a user on a given match.

    Inputs:
    - user (str): username
    - compLevel (CompLevel): CompLevel of match
    - matchNumber (int): matchNumber of match
    - setNumber (int): setNumber of match
    - forRed (bool): if the prediction is for red alliance winning
    - points (int): number of points spent
    """
    timestamp = datetime.now()
    if not getUser(user):
        app.logger.error(f"Couldn't create prediction for {user}: user doesn't exist.")
        abort(400)
    matchData = getMatch(compLevel, matchNumber, setNumber)
    if not matchData:
        app.logger.error(f"Couldn't create prediction for {compLevel}{matchNumber}_{setNumber}: match doesn't exist.")
        abort(400)
    matchData = matchData[0]

    accounts.update_one({"username": user}, {"$set": {f"predictions.{matchData['matchKey']}": {"forRed": forRed, "points": points,"matchComplete": False, "correct": False, "timestamp": timestamp}}, "$inc":{"points": -points}})
    # matches.update_one({"matchKey": matchData["matchKey"]},{"$set":{f"predictions.{user}": {"forRed": forRed, "points": points, "timestamp": timestamp}}, "$inc": {"prizePool.overall": points, f"prizePool.{'red' if forRed else 'blue'}": points}})
    matches.update_one({"matchKey": matchData["matchKey"]},{"$inc": {"prizePool.overall": points, f"prizePool.{'red' if forRed else 'blue'}": points}})
    app.logger.info(f"Created prediction for {user} on {compLevel}{matchNumber}_{setNumber}: {points} for {'Red' if forRed else 'Blue'} Victory.")

def getPredictionAccounts(matchKey: str):
    """
    Returns a list of users who have a prediction for a given match.

    Inputs:
    - matchKey (str): matchKey for match

    Returns:
    - list[dict]: list of dicts of users
    """
    return parseResults(accounts.find({f"predictions.{matchKey}": {"$exists": True}}))

def getPredictionAccountsForAlliance(matchKey: str, forRed: bool):
    """
    Returns a list of users who have a prediction for a given match with a given prediction.

    Inputs:
    - matchKey (str): matchKey for match
    - forRed (bool): if the user predicts red alliance will win

    Returns:
    - list[dict]: list of dicts of users
    """
    return parseResults(accounts.find({f"predictions.{matchKey}.forRed": forRed}))

def payoutPredictions(matchKey: str, forRed: bool):
    matchData = parseResults(matches.find_one({"matchKey": matchKey}))
    correctUsers = getPredictionAccountsForAlliance(matchKey, forRed)
    # incorrectUsers = getPredictionAccountsForAlliance(matchKey, not forRed)
    try:
        redPool = matchData["prizePool"]["red"]
    except KeyError:
        redPool = 0
    try:
        bluePool = matchData["prizePool"]["blue"]
    except KeyError:
        bluePool = 0
    totalPool = matchData["prizePool"]["overall"]

    winningPool = redPool if forRed else bluePool
    
    accounts.update_many({f"predictions.{matchKey}": {"$exists": True}}, {"$set": {f"predictions.{matchKey}.matchCompelete": True}})

    if winningPool <= 0:
        app.logger.info(f"Paid 0 for {'red' if forRed else 'blue'} predictions on {matchKey}")
        return

    for user in correctUsers:
        # payout calculation: (bet/total bets for alliance) * total for all bets
        # = % of red or blue pool * total pool
        payout = round((user["predictions"][matchKey]["points"]/winningPool) * totalPool)
        accounts.update_one({"username": user["username"]}, {"$inc": {"points": payout}, "$set": {f"predictions.{matchKey}.correct": True}})
        app.logger.info(f"Paid {payout} to {user['username']}")
    
    app.logger.info(f"Paid out total of {totalPool} in a ratio of 1:{totalPool/winningPool} for {'red' if forRed else 'blue'} predictions on {matchKey}")
