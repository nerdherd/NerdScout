from array import array
from datetime import datetime
from http.client import HTTPException
import os
import random
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
from app import PaymentRequired
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

def loadFromCacheFile(file: str, path: str = "cache") -> str:
    """
    Loads text data from a cache file.

    Inputs:
    - file (str): file name
    - path (str): path to file, defaults to cache

    Returns:
    - str: file contents
    """
    try:
        with open(os.path.join(root, path, file), "r") as f:
            data = f.read()
    except FileNotFoundError:
        data = ""
    return data

def writeToCacheFile(text: str, file: str, path:str = "cache") -> None:
    """
    Writes text data to a cache file.

    Inputs:
    - text (str): text to save
    - file (str): file name
    - path (str): path to file, defaults to cache
    """
    with open(os.path.join(root, path, file), "w") as f:
        f.write(text)
        app.logger.info(f"wrote to {path}/{file}")


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
    # saves the event key to a file for future use
    writeToCacheFile(event,"recentEventKey")
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
    GETs a schedule from TBA, and adds any matches that are not already in the database. Also saves score breakdowns for completed matches 

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
                matchInDB = parseResults(matches.find_one({"matchKey": match["key"]}))
                if (not "scoreBreakdown" in matchInDB["results"]):
                    matches.update_one({"matchKey": match["key"]},{"$set":{"results.scored":True, "results.postResultTime": match["post_result_time"], "results.actualTime": match["actual_time"], "results.scoreBreakdown": match["score_breakdown"], "results.winningAlliance": match["winning_alliance"]}})
                    app.logger.info(f"Saved new score breakdown for {match['key']}; Now paying predictions.")
                    payoutPredictions(match["key"],match["winning_alliance"] == "red")
                    continue
                if (matchInDB["results"]["postResultTime"] < match["post_result_time"]):
                    matches.update_one({"matchKey": match["key"]},{"$set":{"results.postResultTime": match["post_result_time"], "results.actualTime": match["actual_time"], "results.scoreBreakdown": match["score_breakdown"], "results.winningAlliance": match["winning_alliance"]}})
                    app.logger.info(f"Updated score breakdown for {match['key']}")


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

def saveAlliancesFromTBA(event: str):
    """
    GETs alliance selection data from TBA and stores it in cache/alliances

    Inputs:
    - event (str): event key
    """
    try:
        data = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event}/alliances",
                            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"})
        data = json.loads(data.text)
        if "Error" in data:
            app.logger.error(  # type: ignore
                f"Failed to load alliance data for {event} from The Blue Alliance. API error: {data['Error']}"
            )
            abort(500)
    except:
        app.logger.error(  # type: ignore
            f"Failed to load alliance data for {event} from The Blue Alliance. Network error."
        )
        abort(500)
    saveData = {"rawData": data, "eventKey": event}
    for alliance in data:
        # alliance names are in format "Alliance #"
        saveData[alliance["name"]] = []
        for team in alliance["picks"]:
            try:
                teamNumber = int(team[3:])
            except ValueError:
                app.logger.error(f"Failed to extract team number for {team}")
                continue
            saveData[alliance["name"]].append(teamNumber)
    writeToCacheFile(json.dumps(saveData),"alliances")

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

def updateMatchFromTBA(compLevel: CompLevel, matchNumber: int, setNumber: int) -> bool:
    """
    GETs the data for a given match from TBA and adds scoring information to the database.
    If this is the first time data has been added for the match, predictions are paid out.

    Inputs:
    - compLevel (CompLevel): the match's compLevel
    - matchNumber (int): the match's identification number
    - setNumber (int): the match's set number, usually 1

    Returns:
    - bool: True if score was updated
    """
    matchDataList = getMatch(compLevel, matchNumber, setNumber)
    if not matchDataList:
        abort(400)
    elif len(matchDataList) > 1:
        app.logger.error(f"Error updating scoring data: multiple matches found for {compLevel.value}{matchNumber}, set {setNumber}.")
    matchData = matchDataList[0]
    matchKey = matchData["matchKey"]

    try:
        TBAdata = requests.get(
            f"https://www.thebluealliance.com/api/v3/match/{matchKey}",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        if TBAdata.status_code == 404:
            abort(400)
        elif not TBAdata.ok:
            raise Exception
        TBAdata = json.loads(TBAdata.text)
    except:
        app.logger.error(f"Failed to load data for match {matchKey} from TBA.")
        abort(500)
    if "score_breakdown" in TBAdata:
        if (not "scoreBreakdown" in matchData["results"]):
            matches.update_one({"matchKey": TBAdata["key"]},{"$set":{"results.scored":True, "results.postResultTime": TBAdata["post_result_time"], "results.actualTime": TBAdata["actual_time"], "results.scoreBreakdown": TBAdata["score_breakdown"], "results.winningAlliance": TBAdata["winning_alliance"]}})
            app.logger.info(f"Saved new score breakdown for {TBAdata['key']}; Now paying predictions.")
            payoutPredictions(TBAdata["key"],TBAdata["winning_alliance"] == "red")
            return True
        if (matchData["results"]["postResultTime"] < TBAdata["post_result_time"]):
            matches.update_one({"matchKey": TBAdata["key"]},{"$set":{"results.postResultTime": TBAdata["post_result_time"], "results.actualTime": TBAdata["actual_time"], "results.scoreBreakdown": TBAdata["score_breakdown"], "results.winningAlliance": TBAdata["winning_alliance"]}})
            app.logger.info(f"Updated score breakdown for {TBAdata['key']}")
            return True
    return False
    


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
    userData = getUser(user)
    if not userData:
        app.logger.error(f"Couldn't create prediction for {user}: user doesn't exist.")
        abort(400)
    if userData["points"] < points:
        app.logger.error(f"Couldn't create prediction for {user}: not enough points")
        raise PaymentRequired
    matchData = getMatch(compLevel, matchNumber, setNumber)
    if not matchData:
        app.logger.error(f"Couldn't create prediction for {compLevel}{matchNumber}_{setNumber}: match doesn't exist.")
        abort(400)
    matchData = matchData[0]

    if matchData['matchKey'] in userData['predictions']:
        app.logger.error(f"Couldn't create prediction for {user} in {compLevel}{matchNumber}_{setNumber}: user already has a prediction.")
        abort(403)

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

def payoutPredictions(matchKey: str, forRed: bool) -> None:
    """
    Pays out predictions on a given match.

    Inputs:
    - matchKey (str): The match key of the match to pay out
    - forRed (bool): If red alliance won the match.
    """
    matchData = parseResults(matches.find_one({"matchKey": matchKey}))
    correctUsers = getPredictionAccountsForAlliance(matchKey, forRed)

    if not "prizePool" in matchData:
        app.logger.info(f"No predictions for {matchData['matchKey']}")
        return

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
        app.logger.info(f"Paid out total of 0 in a ratio of 1:infinity for {'red' if forRed else 'blue'} predictions on {matchKey}")
        return

    for user in correctUsers:
        # payout calculation: (bet/total bets for alliance) * total for all bets
        # = % of red or blue pool * total pool
        payout = round((user["predictions"][matchKey]["points"]/winningPool) * totalPool)
        accounts.update_one({"username": user["username"]}, {"$inc": {"points": payout}, "$set": {f"predictions.{matchKey}.correct": True}})
        app.logger.info(f"Paid {payout} to {user['username']}")
    
    app.logger.info(f"Paid out total of {totalPool} in a ratio of 1:{totalPool/winningPool} for {'red' if forRed else 'blue'} predictions on {matchKey}")

def createPickEms(user: str, points: int, m1Red: bool, m2Red: bool, m3Red: bool, m4Red: bool, m5Red: bool, m6Red: bool, m7Red: bool, m8Red: bool, m9Red: bool, m10Red: bool, m11Red: bool, m12Red: bool, m13Red: bool, finalsRed: bool) -> bool:
    """
    Creates pickems for a given user on the double elimination, 8 alliance format.

    Inputs:
    - user (str): username of user
    - points (int): the number of points the user is betting
    - [match]Red: if the user predicts red will win in that match

    Returns:
    - bool: update acknowledged by MongoDB
    """
    # round 1
    bracket = {
        "m1": {
            "red": 1,
            "blue": 8,
            "winner": "red" if m1Red else "blue"
        },
        "m2": {
            "red": 4,
            "blue": 5,
            "winner": "red" if m2Red else "blue"
        },
        "m3": {
            "red": 2,
            "blue": 7,
            "winner": "red" if m3Red else "blue"
        },
        "m4": {
            "red": 3,
            "blue": 6,
            "winner": "red" if m4Red else "blue"
        },
    }
    # round 2
    bracket["m5"] = {
        "red": bracket["m1"]["blue" if m1Red else "red"],
        "blue": bracket["m2"]["blue" if m2Red else "red"],
        "winner": "red" if m5Red else "blue"
    }
    bracket["m6"] = {
        "red": bracket["m3"]["blue" if m3Red else "red"],
        "blue": bracket["m4"]["blue" if m4Red else "red"],
        "winner": "red" if m6Red else "blue"
    }
    bracket["m7"] = {
        "red": bracket["m1"][bracket["m1"]["winner"]],
        "blue": bracket["m2"][bracket["m2"]["winner"]],
        "winner": "red" if m7Red else "blue"
    }
    bracket["m8"] = {
        "red": bracket["m3"][bracket["m3"]["winner"]],
        "blue": bracket["m4"][bracket["m4"]["winner"]],
        "winner": "red" if m8Red else "blue"
    }

    # round 3
    bracket["m9"] = {
        "red": bracket["m7"]["blue" if m7Red else "red"],
        "blue": bracket["m6"][bracket["m6"]["winner"]],
        "winner": "red" if m9Red else "blue"
    }
    bracket["m10"] = {
        "red": bracket["m8"]["blue" if m8Red else "red"],
        "blue": bracket["m5"][bracket["m5"]["winner"]],
        "winner": "red" if m10Red else "blue"
    }

    # round 4
    bracket["m11"] = {
        "red": bracket["m7"][bracket["m7"]["winner"]],
        "blue": bracket["m8"][bracket["m8"]["winner"]],
        "winner": "red" if m11Red else "blue"
    }
    bracket["m12"] = {
        "red": bracket["m10"][bracket["m10"]["winner"]],
        "blue": bracket["m9"][bracket["m9"]["winner"]],
        "winner": "red" if m12Red else "blue"
    }

    # round 5
    bracket["m13"] = {
        "red": bracket["m11"]["blue" if m11Red else "red"],
        "blue": bracket["m12"][bracket["m12"]["winner"]],
        "winner": "red" if m13Red else "blue"
    }

    # finals
    bracket["finals"] = {
        "red": bracket["m11"][bracket["m11"]["winner"]],
        "blue": bracket["m13"][bracket["m13"]["winner"]],
        "winner": "red" if finalsRed else "blue"
    }

    bracket["winner"] = bracket["finals"][bracket["finals"]["winner"]]
    bracket["points"] = points # type: ignore
    bracket["paid"] = False # type: ignore

    updateStatus = accounts.update_one({"username": user}, {"$set": {"pickems": bracket}, "$inc": {"points": -points}}).acknowledged
    if updateStatus:
        app.logger.info(f"Added pickems for {user}.")
    else:
        app.logger.error(f"Failed to add pickems for {user}.")
    return updateStatus

def payPickEms() -> bool:
    app.logger.info("Starting to pay out pickems")
    qual1 = getMatch(CompLevel.QM,1,1)[0]
    updateScheduleFromTBA(qual1["matchKey"].split("_")[0])
    finals2 = getMatch(CompLevel.F,1,1)[0]
    if "scoreBreakdown" not in finals2["results"]:
        app.logger.warning("Failed to pay pickems: finals 2 not scored")
        return False
    m1 = getMatch(CompLevel.SF,1,1)[0]
    m2 = getMatch(CompLevel.SF,1,2)[0]
    m3 = getMatch(CompLevel.SF,1,3)[0]
    m4 = getMatch(CompLevel.SF,1,4)[0]
    m5 = getMatch(CompLevel.SF,1,5)[0]
    m6 = getMatch(CompLevel.SF,1,6)[0]
    m7 = getMatch(CompLevel.SF,1,7)[0]
    m8 = getMatch(CompLevel.SF,1,8)[0]
    m9 = getMatch(CompLevel.SF,1,9)[0]
    m10 = getMatch(CompLevel.SF,1,10)[0]
    m11 = getMatch(CompLevel.SF,1,11)[0]
    m12 = getMatch(CompLevel.SF,1,12)[0]
    m13 = getMatch(CompLevel.SF,1,13)[0]

    finals1 = getMatch(CompLevel.F,1,1)[0]
    finals3 = getMatch(CompLevel.F,1,3)
    if not finals3:
        finals3 = {}
    else:
        finals3 = finals3[0]

    allMatchResults = {
        "m1": m1["results"],
        "m2": m2["results"],
        "m3": m3["results"],
        "m4": m4["results"],
        "m5": m5["results"],
        "m6": m6["results"],
        "m7": m7["results"],
        "m8": m8["results"],
        "m9": m9["results"],
        "m10": m10["results"],
        "m11": m11["results"],
        "m12": m12["results"],
        "m13": m13["results"]
    }
    allMatchBlueCaptains = {
        "m1": m1["teams"]["blue1"],
        "m2": m2["teams"]["blue1"],
        "m3": m3["teams"]["blue1"],
        "m4": m4["teams"]["blue1"],
        "m5": m5["teams"]["blue1"],
        "m6": m6["teams"]["blue1"],
        "m7": m7["teams"]["blue1"],
        "m8": m8["teams"]["blue1"],
        "m9": m9["teams"]["blue1"],
        "m10": m10["teams"]["blue1"],
        "m11": m11["teams"]["blue1"],
        "m12": m12["teams"]["blue1"],
        "m13": m13["teams"]["blue1"],
    }
    allMatchRedCaptains = {
        "m1": m1["teams"]["red1"],
        "m2": m2["teams"]["red1"],
        "m3": m3["teams"]["red1"],
        "m4": m4["teams"]["red1"],
        "m5": m5["teams"]["red1"],
        "m6": m6["teams"]["red1"],
        "m7": m7["teams"]["red1"],
        "m8": m8["teams"]["red1"],
        "m9": m9["teams"]["red1"],
        "m10": m10["teams"]["red1"],
        "m11": m11["teams"]["red1"],
        "m12": m12["teams"]["red1"],
        "m13": m13["teams"]["red1"],
    }
    allianceDict = {
        str(allMatchRedCaptains["m1"]): 1,
        str(allMatchBlueCaptains["m1"]): 8,
        str(allMatchRedCaptains["m2"]): 4,
        str(allMatchBlueCaptains["m2"]): 5,
        str(allMatchRedCaptains["m3"]): 2,
        str(allMatchBlueCaptains["m3"]): 7,
        str(allMatchRedCaptains["m4"]): 3,
        str(allMatchBlueCaptains["m4"]): 6,
    }
    round1Picks = ["m1","m2","m3","m4"]
    round2Picks = ["m5","m6","m7","m8"]
    round3Picks = ["m9","m10"]
    round4Picks = ["m11","m12"]
    round5Picks = ["m13"]

    finalsRedCaptain = finals1["teams"]["red1"]
    finalsBlueCaptain = finals1["teams"]["blue1"]
    finals1Winner = finals1["results"]["winningAlliance"]
    finals2Winner = finals2["results"]["winningAlliance"]
    if "winningAlliance" in finals3:
        finals3Winner = finals3["results"]["winningAlliance"]
    else:
        finals3Winner = None
    
    if finals1Winner == finals2Winner:
        finalsWinner = finals1Winner
    elif not finals3Winner:
        app.logger.error("Failed to pay out pickems: finals3 winner not found and finals not clinched.")
        return False
    else:
        finalsWinner = finals3Winner

    users = accounts.find({"pickems": {"$exists": True}})

    for user in users:
        if user["pickems"]["paid"]:
            continue
        points = 0
        userPickems = user["pickems"]
        pointsSpent = userPickems["points"]
        

        for pick in round1Picks:
            realWinningAlliance = allianceDict[str(allMatchRedCaptains[pick])] if allMatchResults[pick]["winningAlliance"] == "red" else allianceDict[str(allMatchBlueCaptains[pick])]
            if userPickems[pick][userPickems[pick]["winner"]] == realWinningAlliance:
                app.logger.info(f"Correct pick for {realWinningAlliance} in {pick} for {user['username']}")
                points += int(pointsSpent * 0.2)
        for pick in round2Picks:
            realWinningAlliance = allianceDict[str(allMatchRedCaptains[pick])] if allMatchResults[pick]["winningAlliance"] == "red" else allianceDict[str(allMatchBlueCaptains[pick])]
            if userPickems[pick][userPickems[pick]["winner"]] == realWinningAlliance:                
                app.logger.info(f"Correct pick for {realWinningAlliance} in {pick} for {user['username']}")
                points += int(pointsSpent * 0.4)
        for pick in round3Picks:
            realWinningAlliance = allianceDict[str(allMatchRedCaptains[pick])] if allMatchResults[pick]["winningAlliance"] == "red" else allianceDict[str(allMatchBlueCaptains[pick])]
            if userPickems[pick][userPickems[pick]["winner"]] == realWinningAlliance:
                app.logger.info(f"Correct pick for {realWinningAlliance} in {pick} for {user['username']}")
                points += int(pointsSpent * 0.6)
        for pick in round4Picks:
            realWinningAlliance = allianceDict[str(allMatchRedCaptains[pick])] if allMatchResults[pick]["winningAlliance"] == "red" else allianceDict[str(allMatchBlueCaptains[pick])]
            if userPickems[pick][userPickems[pick]["winner"]] == realWinningAlliance:
                app.logger.info(f"Correct pick for {realWinningAlliance} in {pick} for {user['username']}")
                points += int(pointsSpent * 0.8)
        for pick in round5Picks:
            realWinningAlliance = allianceDict[str(allMatchRedCaptains[pick])] if allMatchResults[pick]["winningAlliance"] == "red" else allianceDict[str(allMatchBlueCaptains[pick])]
            if userPickems[pick][userPickems[pick]["winner"]] == realWinningAlliance:
                app.logger.info(f"Correct pick for {realWinningAlliance} in {pick} for {user['username']}")
                points += pointsSpent
        
        realFinalsWinner = allianceDict[str(finalsRedCaptain)] if finalsWinner == "red" else allianceDict[str(finalsBlueCaptain)]
        if userPickems["winner"] == realFinalsWinner:
            points += int(pointsSpent * 1.2)
            app.logger.info(f"Correct pick for {realFinalsWinner} in finals for {user['username']}")
        
        updateStatus = accounts.update_one({"username": user["username"]}, {"$inc": {"points": points}, "$set": {"pickems.paid": True}}).acknowledged
        if updateStatus:
            app.logger.info(f"Paid {points} for {user['username']}'s pickems")
        else:
            app.logger.info(f"Failed to pay for {user['username']}'s pickems")
    return True

def createTestTBABreakdown() -> dict:
    """
    Creates a random score breakdown for one alliance.
    Game specific, currently for REBUILT.

    Returns:
    - dict: score breakdown
    """
    # this part is game specific. as of january 2026, this is for REBUILT.
    autoCount = random.randint(0,40)
    endgameCount = random.randint(0,40)
    firstShift = random.random() > 0.5
    shift1Count = random.randint(0,40)
    shift2Count = random.randint(0,40)
    shift3Count = random.randint(0,40)
    shift4Count = random.randint(0,40)
    transitionCount = random.randint(0,40)
    scoreBreakdown = {
        "adjustPoints": random.randint(0,10),
        "autoTowerPoints": 15 * random.randint(0,3),
        "autoTowerRobot1":f"#{random.randint(0,3)}",
        "autoTowerRobot2": f"#{random.randint(0,3)}",
        "autoTowerRobot3": f"#{random.randint(0,3)}",
        "endGameTowerPoints": 10 * random.randint(0,9),
        "endGameTowerRobot1": f"#{random.randint(0,3)}",
        "endGameTowerRobot2": f"#{random.randint(0,3)}",
        "endGameTowerRobot3": f"#{random.randint(0,3)}",
        "energizedAchieved": random.random() > 0.5,
        "foulPoints": random.randint(0,20),
        "g206Penalty": random.random() > 0.5,
        "hubScore":{
            "autoCount": autoCount,
            "autoPoints": autoCount,
            "endgameCount": endgameCount,
            "endgamePoints": endgameCount,
            "shift1Count": shift1Count,
            "shift1Points": shift1Count if firstShift else 0,
            "shift2Count": shift2Count,
            "shift2Points": shift2Count if  not firstShift else 0,
            "shift3Count": shift3Count,
            "shift3Points": shift3Count if firstShift else 0,
            "shift4Count": shift4Count,
            "shift4Points": shift4Count if  not firstShift else 0,
            "teleopCount": transitionCount + shift1Count + shift2Count + shift3Count + shift4Count + endgameCount,
            "teleopPoints": transitionCount + (shift1Count if firstShift else shift2Count) + (shift3Count if firstShift else shift4Count) + endgameCount,
            "totalCount": transitionCount + shift1Count + shift2Count + shift3Count + shift4Count + endgameCount + autoCount,
            "totalPoints": transitionCount + (shift1Count if firstShift else shift2Count) + (shift3Count if firstShift else shift4Count) + endgameCount + autoCount,
        },
        "majorFoulCount": random.randint(0,10),
        "minorFoulCount": random.randint(0,100),
        "rp": random.randint(0,6),
        "superchargedAchieved": random.random() > 0.3,
        "totalAutoPoints": random.randint(0,100),
        "totalPoints": random.randint(0,250),
        "totalTeleopPoints": random.randint(0,150),
        "totalTowerPoints": (10 * random.randint(0,9)) + (15 * random.randint(0,3)),
        "traversalAchieved": random.random() > 0.5
    }
    
    return scoreBreakdown

def addTestTBAData(compLevel: CompLevel, matchNumber: int, setNumber: int) -> bool:
    """
    adds randomized fake TBA data to the database and pays out predictions.

    Inputs:
    - compLevel (CompLevel): competition level of match
    - matchNumber (int): match number
    - setNumber (int): set number

    Returns:
    - bool: success
    """
    matchDataList = getMatch(compLevel, matchNumber, setNumber)
    if not matchDataList:
        abort(400)
    elif len(matchDataList) > 1:
        app.logger.error(f"Error updating scoring data: multiple matches found for {compLevel.value}{matchNumber}, set {setNumber}.")
    matchData = matchDataList[0]
    matchKey = matchData["matchKey"]

    TBAdata = {
        "key": matchKey,
        "comp_level": compLevel.value,
        "set_number": setNumber,
        "match_number": matchNumber,
        "alliances": {"placeholder": '"we dont use this right now" - gold ship'},
        "winning_alliance": "red" if random.random() > 0.5 else "blue",
        "event_key": "abaca",
        "time": int(time()),
        "actual_time": int(time()) - random.randint(0,120),
        "predicted_time": int(time()),
        "post_result_time": int(time()),
        "score_breakdown": {
            "red": createTestTBABreakdown(),
            "blue": createTestTBABreakdown(),
            },
        "videos": [
            {
                "type": "youtube",
                "key": "https://youtu.be/AcVp_yl5QZs"
            },
        ],
    }
    if "score_breakdown" in TBAdata:
        if (not "scoreBreakdown" in matchData["results"]):
            matches.update_one({"matchKey": TBAdata["key"]},{"$set":{"results.scored":True, "results.postResultTime": TBAdata["post_result_time"], "results.actualTime": TBAdata["actual_time"], "results.scoreBreakdown": TBAdata["score_breakdown"], "results.winningAlliance": TBAdata["winning_alliance"]}})
            app.logger.info(f"Saved new score breakdown for {TBAdata['key']}; Now paying predictions.")
            payoutPredictions(TBAdata["key"],TBAdata["winning_alliance"] == "red")
            return True
        if (matchData["results"]["postResultTime"] < TBAdata["post_result_time"]):
            matches.update_one({"matchKey": TBAdata["key"]},{"$set":{"results.postResultTime": TBAdata["post_result_time"], "results.actualTime": TBAdata["actual_time"], "results.scoreBreakdown": TBAdata["score_breakdown"], "results.winningAlliance": TBAdata["winning_alliance"]}})
            app.logger.info(f"Updated score breakdown for {TBAdata['key']}")
            return True
    return False