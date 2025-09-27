from enum import Enum
import os
from typing import List
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
import filetype
import statistics

app = Flask(__name__)
root = os.path.dirname(__file__)

class Station(Enum):
    RED1 = "red1"
    RED2 = "red2"
    RED3 = "red3"
    BLUE1 = "blue1"
    BLUE2 = "blue2"
    BLUE3 = "blue3"


STATION_LIST = [station.value for station in Station]


class StartingPosition(Enum):
    BLUE = 1
    TOP = 1

    CENTER = 2
    MIDDLE = 2

    RED = 3
    BOTTOM = 3


class EndPosition(Enum):
    NONE = 0
    PARK = 1
    SHALLOW = 2
    DEEP = 3


class CompLevel(Enum):
    QM = "qm"
    QUALIFYING = "qm"

    EF = "ef"

    QF = "qf"

    SF = "sf"
    PLAYOFF = "sf"

    F = "f"
    FINAL = "f"

STAT_CODES = ["mean", "median", "mode", "highest", "lowest"]

TBA_KEY = open(os.path.join(root, "secrets/theBlueAlliance"), "r").read()
# TODO: add all text descriptions for all match types
compLevelText = {"qm": "Qualifying", "sf": "Playoff", "f": "Final"}
freeEndpoints = frozenset(
    ["login", "newUserPage", "static", "index", "logout"]
)  # endpoints that shouldn't require signing in


def calculateScore(
    autoLeave: bool,
    autoReef: List[int],
    teleReef: List[int],
    autoProcessor: int,
    teleProcessor: int,
    autoNet: int,
    teleNet: int,
    endPos: int,
    minorFouls: int,
    majorFouls: int,
):
    score = 0

    score += 3 if autoLeave else 0

    score += 3 * autoReef[0]
    score += 4 * autoReef[1]
    score += 6 * autoReef[2]
    score += 7 * autoReef[3]

    score += 2 * teleReef[0]
    score += 3 * teleReef[1]
    score += 4 * teleReef[2]
    score += 5 * teleReef[3]

    score += 6 * autoProcessor
    score += 6 * teleProcessor

    score += 4 * autoNet
    score += 4 * teleNet

    score += (
        2
        if endPos == EndPosition.PARK.value
        else (
            6
            if endPos == EndPosition.SHALLOW.value
            else 12 if endPos == EndPosition.DEEP.value else 0
        )
    )

    score -= 2 * minorFouls
    score -= 6 * majorFouls

    return score


def isImage(file):
    try:
        result = filetype.guess_extension(file)
        return False if not (result == "png" or result == "jpg") else result
    except Exception as e:
        app.logger.info(f"Failed to check file type for {request.remote_addr}: {e}")  # type: ignore
        return False
    
# these functions use data from getResults(int)
def getListOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    scores: list = []
    for item in data:
        try:
            score = item["results"][-1][key]
            if type(score) == list:
                score = score[reefLevel]
            scores.append(int(score))
        except:
            app.logger.error(f'Failed to get data for key {key} in data "{item}"')  # type: ignore
            abort(500)
    return scores

def getMeanOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    scores: list = getListOfScoringCategory(data,key,reefLevel)
    if not scores:
        return 0.0
    return float(statistics.mean(scores))

def getMedianOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    scores: list = getListOfScoringCategory(data,key,reefLevel)
    if not scores:
        return 0.0
    return float(statistics.median(scores))

def getModeOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    scores: list = getListOfScoringCategory(data,key,reefLevel)
    if not scores:
        return 0
    return int(statistics.median(scores))

def getMatchWithHighestValue(data: list, key: str, reefLevel: int = 0):
    highestValue: int = -1
    matchKey: str = ""
    matchNumber: int = 0
    compLevel: str = ""
    setNumber: int = 0
    displayName: str = ""
    for match in data:
        value = match["results"][-1][key]
        if type(value) == list:
            value = value[reefLevel]
        value = int(value)
        if value > highestValue:
            highestValue = value
            matchKey = match["matchKey"]
            matchNumber = match["matchNumber"]
            compLevel = match["compLevel"]
            setNumber = match["setNumber"]
            displayName = match["displayName"]

    highestValue = 0 if highestValue == -1 else highestValue
    highestMatch = {
        "value": highestValue,
        "category": key,
        "matchKey": matchKey,
        "matchNumber": matchNumber,
        "compLevel": compLevel,
        "setNumber": setNumber,
        "displayName": displayName,
        "reefLevel": reefLevel,
    }
    return highestMatch

def getMatchWithLowestValue(data: list, key: str, reefLevel: int = 0):
    lowestValue: int = 9999
    matchKey: str = ""
    matchNumber: int = 0
    compLevel: str = ""
    setNumber: int = 0
    displayName: str = ""
    for match in data:
        value = match["results"][-1][key]
        if type(value) == list:
            value = value[reefLevel]
        value = int(value)
        if value < lowestValue:
            lowestValue = value
            matchKey = match["matchKey"]
            matchNumber = match["matchNumber"]
            compLevel = match["compLevel"]
            setNumber = match["setNumber"]
            displayName = match["displayName"]
    
    lowestValue = 0 if lowestValue == 9999 else lowestValue
    lowestMatch = {
        "value": lowestValue,
        "category": key,
        "matchKey": matchKey,
        "matchNumber": matchNumber,
        "compLevel": compLevel,
        "setNumber": setNumber,
        "displayName": displayName,
        "reefLevel": reefLevel,
    }
    return lowestMatch

def getAllStatsForCategory(data: list, key: str, reefLevel: int = 0):
    scores: list = getListOfScoringCategory(data,key,reefLevel)
    if not scores:
        return{
            "mean": 0,
            "median": 0,
            "mode": 0,
            "lowestMatch":getMatchWithLowestValue(data,key,reefLevel),
            "highestMatch": getMatchWithHighestValue(data,key,reefLevel),
        }
    return {
        "mean": float(statistics.mean(scores)),
        "median": float(statistics.median(scores)),
        "mode": int(statistics.mode(scores)),
        "lowestMatch": getMatchWithLowestValue(data,key,reefLevel),
        "highestMatch": getMatchWithHighestValue(data,key,reefLevel),
    }