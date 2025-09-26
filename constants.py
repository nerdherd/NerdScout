from enum import Enum
import os
from typing import List
from flask import Flask, abort, redirect, render_template, request, session, url_for, Blueprint
import filetype

app = Flask(__name__)


class Station(Enum):
    RED1 = "red1"
    RED2 = "red2"
    RED3 = "red3"
    BLUE1 = "blue1"
    BLUE2 = "blue2"
    BLUE3 = "blue3"


STATION_LIST = [station.value for station in Station]


class StartingPosition(Enum):
    TOP = 1
    MIDDLE = 2
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

root = os.path.dirname(__file__)
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
        app.logger.info(f"Failed to check file type for {request.remote_addr}: {e}") #type: ignore
        return False
    
def getAverageOfScoringCategory(data:list, key:str):
    average:float = 0
    for item in data:
        try:
            average += item["results"][-1][key]
        except:
            app.logger.error(f'Failed to get average for key {key} in data "{data}"') #type: ignore
            abort(500)
    average /= len(data)
    return average