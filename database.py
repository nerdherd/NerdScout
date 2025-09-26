from array import array
from http.client import HTTPException
import os
import re
import filetype
import urllib.parse
from flask import Flask, abort, redirect, render_template, request, session, url_for, Blueprint
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
    app.logger.info( # type: ignore
        f"New match scheduled: Match {compLevel.value}{matchNumber} between red alliance {red1}, {red2}, {red3} and blue alliance {blue1}, {blue2}, {blue3}."
    )

def addMatchFromTBA(match: dict):
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
        app.logger.error( #type: ignore
            f"Unable to load match from The Blue Alliance. Aborting. Error: {e}"
        )
        abort(500)

def sortMatches(matches:list):
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

def sortTeams(teams:list):
    sortedTeams = sorted(teams,key = lambda team: team["number"])
    return sortedTeams

def loadScheduleFromTBA(event:str):
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
        app.logger.error(f"Failed to load match data for {event} from TBA.") #type: ignore
        abort(500)
    return data

def addScheduleFromTBA(event: str):
    if matches.count_documents({}) != 0:
        abort(409)
    data = loadScheduleFromTBA(event)
    for match in data:
        addMatchFromTBA(match)
    return "ok"

def updateScheduleFromTBA(event: str):
    newData = loadScheduleFromTBA(event)
    for match in newData:
        results = matches.count_documents({"matchKey":match["key"]})
        if results == 0:
            addMatchFromTBA(match)

def addTeam(number: int, longName: str, shortName: str, comment: list = []):
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
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/teams/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        data = json.loads(data.text)
        if "Error" in data:
            app.logger.error( #type: ignore
                f"Failed to load team data for {event} from The Blue Alliance. API error: {data['Error']}"
            )
            abort(500)
    except:
        app.logger.error( #type: ignore
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
            app.logger.error( #type: ignore
                f"Failed to load team data for {event} from The Blue Alliance. {e}"
            )
            abort(500)

# This always outputs an array, in case there are multiple matches with the same number
def getMatch(compLevel: CompLevel, matchNumber: int, setNumber: int):
    searchDict = {
            "compLevel": compLevel.value,
            "matchNumber": matchNumber,
            "setNumber": setNumber,
        }
    with matches.find(searchDict) as results:
        parsedResults = parseResults(results)
    return parsedResults

def getAllMatches():
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
        app.logger.info( #type: ignore
            f"Failed to score robot {startPos.value} for match {matchNumber} by {scout}: Match does not exist."
        )
        return False
    app.logger.info(f"Robot {station.value} scored for match {matchNumber} by {scout}.") #type: ignore
    return True

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

def addTeamImage(data,team:int,user:str):
    extension = isImage(data)
    if not extension:
        abort(415)
    teamInfo = parseResults(teams.find_one({"number":team}))
    fileLocation = f"teamImages/{team}_{len(teamInfo['images'])}.{extension}"
    open(os.path.join(root,"static/"+fileLocation),"wb").write(data)
    teams.update_one({"number": team}, 
                     {"$push":{
                        "images": {
                            "location":fileLocation,
                            "scout":user,
                            }
                        }
                      }
                     )
    
def addComment(team:int,comment:str,user:str):
    teams.update_one(
        {"number":team},
        {"$push": {"comments":{"comment":comment,"user":user}}}
    )

def getTeam(team:int):
    result = teams.find_one(
        {
            "number":team
        }
    )
    parsedResults = parseResults(result)
    return parsedResults

def getTeamMatches(team:int):
    result = matches.find({"$or":[
        {"teams.red1":team},
        {"teams.red2":team},
        {"teams.red3":team},
        {"teams.blue1":team},
        {"teams.blue2":team},
        {"teams.blue3":team},
    ]})
    parsedResults = parseResults(result)
    result.close()
    return parsedResults

def getTeamStation(team:int, match:dict):
    station = None
    for key, value in match["teams"].items():
        if value == team:
            station = key
            break
    return station

def getTeamScoredMatches(team:int):
    result = getTeamMatches(team)
    filteredResults = []
    for match in result:
        station = getTeamStation(team, match)
        if not station:
            app.logger.error(f'Could not get scored matches for {team}: Failed to get station from match {match["compLevel"]}{match["matchNumber"]} set {match["setNumber"]}.') #type: ignore
            abort(500)
        if station in match["results"]:
            filteredResults.append(match)
    return filteredResults

# strips out the teams array and all other teams' results
def getTeamResults(team:int):
    matches = getTeamMatches(team)
    results = []
    for match in matches:
        station = getTeamStation(team, match)
        if not station:
            app.logger.error(f'Could not get results for {team}: Failed to get station from match {match["compLevel"]}{match["matchNumber"]} set {match["setNumber"]}.') #type: ignore
            abort(500)
        if station in match["results"]:
            resultArray = match["results"][station]
            result = {"results":resultArray}
            result["matchNumber"] = match["matchNumber"]
            result["compLevel"] = match["compLevel"]
            result["setNumber"] = match["setNumber"]
            result["matchKey"] = match["matchKey"]
            result["displayName"] = match["displayName"]
            results.append(result)
    return results

def getAllTeams():
    with teams.find({}) as results:
        parsedResults = parseResults(results)
    return parsedResults

def getAllUsers():
    return parseResults(accounts.find({}))

def isAdmin(username: str):
    return parseResults(accounts.find_one({"username": username}))["admin"]

def getUser(username: str):
    user = accounts.find_one({"username": username})
    return user


# converts database results to JSON
# the default functions get stuck on ObjectID objects
def parseResults(data):
    return json.loads(json_util.dumps(data))