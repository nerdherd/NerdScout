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
keyDisplayNames = {
    "matchNumber": "Match Number",
    "setNumber": "Set Number",
    "compLevel": "Competition Level",
    "matchKey": "Match Key",
    "displayName": "Display Name",
    "teams": "Teams",
    "red1": "Red 1",
    "red2": "Red 2",
    "red3": "Red 3",
    "blue1": "Blue 1",
    "blue2": "Blue 2",
    "blue3": "Blue 3",
    "results": "Results",
    "scored": "Scored",
    "startPos": "Starting Position",
    "autoLeave": "Auto Leave",
    "autoReef": "Reef Auto",
    "autoReefL1": "Reef Auto L1",
    "autoReefL2": "Reef Auto L2",
    "autoReefL3": "Reef Auto L3",
    "autoReefL4": "Reef Auto L4",
    "autoReefMiss": "Reef Auto Missed",
    "teleReef": "Reef Tele-Op",
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
    "endPosSuccess": "Succeeded End Position",
    "minorFouls": "Minor Fouls",
    "majorFouls": "Major Fouls",
    "score": "Score Impact",
    "comment": "Comment",
    "scout": "Scout",
}


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
    """
    Calculate the total score from scouted values.
    
    Should change every year.
    
    Inputs:
    - Self explanatory 
    
    Outputs:
    - int: total score, minus points from fouls
    
    """
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

    score += 2 * autoProcessor
    score += 2 * teleProcessor

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
    """
    Checks if the provided file is an image (png or jpg)
    
    Inputs:
    - file (any): the object to test
    
    Outputs:
    - Boolean: whether or not the file is a png or a jpg
    """
    try:
        result = filetype.guess_extension(file)
        return False if not (result == "png" or result == "jpg") else result
    except Exception as e:
        app.logger.info(f"Failed to check file type for {request.remote_addr}: {e}")  # type: ignore
        return False


# these functions use data from getTeamResults(int)
def getListOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    """
    Gets a list of all of the scores in a specific category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - List[int]: list of all of the scores from the data
    """
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
    """
    Gets the mean of a specific scoring category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - float: the mean of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, reefLevel)
    if not scores:
        return 0.0
    return float(statistics.mean(scores))


def getMedianOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    """
    Gets the median of a specific scoring category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - float: the median of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, reefLevel)
    if not scores:
        return 0.0
    return float(statistics.median(scores))


def getModeOfScoringCategory(data: list, key: str, reefLevel: int = 0):
    """
    Gets the mode of a specific scoring category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - float: the mode of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, reefLevel)
    if not scores:
        return 0
    return int(statistics.median(scores))


def getMatchWithHighestValue(data: list, key: str, reefLevel: int = 0):
    """
    Gets the highest value, and the match it was from, of a specific scoring category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - dict: Dictionary containing the highest value, along with the match information
    """
    highestValue: int = -9999999999999
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

    highestValue = 0 if highestValue == -9999999999999 else highestValue
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
    """
    Gets the lowest value, and the match it was from, of a specific scoring category for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - dict: Dictionary containing the lowest value, along with the match information
    """
    lowestValue: int = 9999999999999
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

    lowestValue = 0 if lowestValue == 9999999999999 else lowestValue
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
    """
    Gets all of the different stats for a scoring category (mean, median, mode, highest, lowest) for a team
    
    Should be edited every year (reefLevel).
    
    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - reefLevel (int): the specific reef level to get, if getting scores for reef. Defaults to 0, and doesn't do anything if key isn't reef
    
    Returns:
    - dict: Dictionary containing all five stats
    """
    scores: list = getListOfScoringCategory(data, key, reefLevel)
    if not scores:
        return {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "lowestMatch": getMatchWithLowestValue(data, key, reefLevel),
            "highestMatch": getMatchWithHighestValue(data, key, reefLevel),
        }
    return {
        "mean": float(statistics.mean(scores)),
        "median": float(statistics.median(scores)),
        "mode": int(statistics.mode(scores)),
        "lowestMatch": getMatchWithLowestValue(data, key, reefLevel),
        "highestMatch": getMatchWithHighestValue(data, key, reefLevel),
    }
