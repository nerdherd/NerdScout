from enum import Enum
import os
from flask import (
    Flask,
    abort,
    request,
)
import filetype
import statistics
from werkzeug.exceptions import HTTPException

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


class EndPositionReefscape(Enum):
    NONE = 0
    PARK = 1
    SHALLOW = 2
    DEEP = 3


class EndPositionRebuilt(Enum):
    L1 = 1
    L2 = 2
    L3 = 3
    NONE = 0


FMSEndPositionRebuilt = {
    "Level1": EndPositionRebuilt.L1,
    "Level2": EndPositionRebuilt.L2,
    "Level3": EndPositionRebuilt.L3,
    "None": EndPositionRebuilt.NONE,
}


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


class PaymentRequired(HTTPException):
    code = 402
    description = "Payment Required"


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
def getListOfScoringCategory(data: list, key: str, index: int = 0):
    """
    Gets a list of all of the scores in a specific category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

    Returns:
    - List[int]: list of all of the scores from the data
    """
    scores: list = []
    for item in data:
        try:
            score = item["results"][-1][key]
            if type(score) == list:
                score = score[index]
            scores.append(int(score))
        except:
            app.logger.error(f'Failed to get data for key {key} in data "{item}"')  # type: ignore
            abort(500)
    return scores


def getMeanOfScoringCategory(data: list, key: str, index: int = 0):
    """
    Gets the mean of a specific scoring category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

    Returns:
    - float: the mean of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, index)
    if not scores:
        return 0.0
    return float(statistics.mean(scores))


def getMedianOfScoringCategory(data: list, key: str, index: int = 0):
    """
    Gets the median of a specific scoring category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

    Returns:
    - float: the median of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, index)
    if not scores:
        return 0.0
    return float(statistics.median(scores))


def getModeOfScoringCategory(data: list, key: str, index: int = 0):
    """
    Gets the mode of a specific scoring category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

    Returns:
    - float: the mode of the scoring category
    """
    scores: list = getListOfScoringCategory(data, key, index)
    if not scores:
        return 0
    return int(statistics.median(scores))


def getMatchWithHighestValue(data: list, key: str, index: int = 0):
    """
    Gets the highest value, and the match it was from, of a specific scoring category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

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
            value = value[index]
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
        "index": index,
    }
    return highestMatch


def getMatchWithLowestValue(data: list, key: str, index: int = 0):
    """
    Gets the lowest value, and the match it was from, of a specific scoring category for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

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
            value = value[index]
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
        "index": index,
    }
    return lowestMatch


def getAllStatsForCategory(data: list, key: str, index: int = 0):
    """
    Gets all of the different stats for a scoring category (mean, median, mode, highest, lowest) for a team

    Inputs:
    - data (list[dict]): a list with all of a team's match results. From getTeamResults
    - key (str): the key of the scoring category to get
    - index (int): if the data is a list, then what index to get. Defaults to 0, and does nothing if not a list.

    Returns:
    - dict: Dictionary containing all five stats
    """
    scores: list = getListOfScoringCategory(data, key, index)
    if not scores:
        return {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "lowestMatch": getMatchWithLowestValue(data, key, index),
            "highestMatch": getMatchWithHighestValue(data, key, index),
        }
    return {
        "mean": float(statistics.mean(scores)),
        "median": float(statistics.median(scores)),
        "mode": int(statistics.mode(scores)),
        "lowestMatch": getMatchWithLowestValue(data, key, index),
        "highestMatch": getMatchWithHighestValue(data, key, index),
    }
