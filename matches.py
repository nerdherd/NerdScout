# pull matches from TBA

from enum import Enum
import json
import os
import requests

root = os.path.dirname(__file__)

TBA_KEY = open(os.path.join(root, "secrets/theBlueAlliance"), "r").read()

class CompLevel(Enum):
    QM = "qm"
    QUALIFYING = "qm"

    EF = "ef"

    QF = "qf"

    SF = "sf"
    PLAYOFF = "sf"

    F = "f"
    FINAL = "f"

def getSchedule(event: str):
    try:
        data = requests.get(
            f"https://www.thebluealliance.com/api/v3/event/{event}/matches/simple",
            headers={"X-TBA-Auth-Key": TBA_KEY, "User-Agent": "Nerd Scout"},
        )
        if data.status_code == 404:
            print("Failed: 404 returned")
        elif not data.ok:
            raise Exception
        data = json.loads(data.text)
    except:
        print(f"Failed to load match data for {event} from TBA.")
    return data

def sortMatches(matches: list):
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

def saveSchedule(event: str):
    data = []
    rawData = getSchedule(event)
    for match in rawData:
        matchNumber = match["match_number"]
        setNumber = match["set_number"]
        compLevel = CompLevel(match["comp_level"])
        if compLevel == CompLevel.QUALIFYING:
            displayName = f"Qualifying {matchNumber}"
        elif compLevel == CompLevel.PLAYOFF:
            displayName = f"Playoff {setNumber}"
        elif compLevel == CompLevel.FINAL:
            displayName = f"Final {matchNumber}"
        else:
            displayName = f"{compLevel.value} {matchNumber}"
        curMatch={
            "matchNumber": matchNumber,
            "setNumber": setNumber,
            "compLevel": match["comp_level"],
            "matchKey": match["key"],
            "displayName": displayName,
            "teams": {
                "red1": int(match["alliances"]["red"]["team_keys"][0][3:]),
                "red2": int(match["alliances"]["red"]["team_keys"][1][3:]),
                "red3": int(match["alliances"]["red"]["team_keys"][2][3:]),
                "blue1": int(match["alliances"]["blue"]["team_keys"][0][3:]),
                "blue2": int(match["alliances"]["blue"]["team_keys"][1][3:]),
                "blue3": int(match["alliances"]["blue"]["team_keys"][2][3:]),
            },
        }
        data.append(curMatch)
    return sortMatches(data)

cur_event = input("Enter event code: ")

schedule = saveSchedule(cur_event)

with open(os.path.join(root, cur_event+"-schedule.json"),"w") as f:
    f.write(str(schedule).replace("'",'"'))