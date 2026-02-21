from typing import List
from constants import *
from constants import Station, getMeanOfScoringCategory
from database import *
from pymongo.collection import Collection

from database import Station, getMeanOfScoringCategory


class Game:
    """
    Game Superclass

    This shouldn't be used; all functions should be replaced.
    """

    def __init__(self, matches: Collection, teams: Collection):
        self.keyDisplayNames = {}
        self.matches = matches
        self.teams = teams
        self.teamRankOptions = {}
        self.teamTableDisplayNames = {}
        self.matchTableDisplayNames = {}
        self.cannedComments = []
        self.pitScoutAutoCapabilities = tuple()
        self.pitScoutTeleCapabilities = tuple()
        raise NotImplementedError("Game Superclass __init__ used")

    def calculateScore(self) -> int:
        """
        Calculate the total score from scouted values.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - Depends

        Outputs:
        - int: total score, minus points from fouls

        """
        raise NotImplementedError("Game Superclass calculateScore used")
        # return 0

    def scoreRobotInMatch(self) -> bool:
        """
        Scores one robot in a match.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - self explanitory

        Returns:
        - Boolean: if the robot was successfully scored
        """
        raise NotImplementedError("Game Superclass scoreRobotInMatch used")
        # return False

    def calculateScoreFromData(
        self, matchData: dict, team: Station, edit: int = -1
    ) -> int:
        """
        Gets a robot's result from the database and scores it.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - matchData (dict): a match dict
        - team (Station): the station to score
        - edit (int): which revision to score, defaults to the latest

        Returns:
        - int: calculated score
        """
        raise NotImplementedError("Game Superclass calculateScoreFromData used")
        # return 0

    def calculateAverageAllianceScore(
        self, team1: int, team2: int, team3: int, calc=getMeanOfScoringCategory
    ) -> dict | None:
        """
        Calculates a hypothetical alliance score of three teams using their average results in each category.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - team1 (int): team number 1
        - team2 (int): team number 2
        - team3 (int): team number 3
        - calc (function): the static function to use, defaults to mean

        Returns:
        - dict or none: dict of predicted results, or None if any teams are not found.
        """
        raise NotImplementedError("Game Superclass calculateAverageAllianceScore used")
        # return None

    def calculateMinMaxAllianceScore(
        self, team1: int, team2: int, team3: int, maximum: bool = True
    ) -> dict | None:
        """
        Calculates a hypothetical alliance score of three teams using their minimum or maximum results in each category.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - team1 (int): team number 1
        - team2 (int): team number 2
        - team3 (int): team number 3
        - maximum (bool): True uses maximum, False uses minimum, defaults to True

        Returns:
        - dict or none: dict of predicted results, or None if any teams are not found.
        """
        raise NotImplementedError("Game Superclass calcualteMinMaxAllianceScore used")
        # return None

    def getAllStats(self, team: int) -> dict:
        """
        Calculates all stats for every single scoring category.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - team (int): Team number

        Returns:
        - dict: dict of every scoring category with every stat
        """
        raise NotImplementedError("Game Superclass getAllStats used")
        # return {}

    def calculateAllianceFromMatches(
        self,
        team1: int,
        match1: list,
        team2: int,
        match2: list,
        team3: int,
        match3: list,
    ) -> dict:
        """
        Adds together results for three teams from given match data to predict their performance as an alliance.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - team1 (int): team 1 number
        - match1 (list): match data for team 1
        - team2 (int): team 2 number
        - match2 (list): match data for team 2
        - team3 (int): team 3 number
        - match3 (list): match data for team 3

        Returns:
        - dict: predicted results dict
        """
        raise NotImplementedError("Game Superclass calculateAllianceFromMatches used")
        # return {}


class Reefscape(Game):
    def __init__(self, matches: Collection, teams: Collection):
        self.keyDisplayNames = {
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
        self.matches = matches
        self.teams = teams
        self.teamRankOptions = {
            "Score Impact": "score,0",
            "Starting Position": "startPos,0",
            "Auto Leave": "autoLeave,0",
            "Reef Auto": "autoReef,0",
            "Reef Auto L1": "autoReef,0",
            "Reef Auto L2": "autoReef,1",
            "Reef Auto L3": "autoReef,2",
            "Reef Auto L4": "autoReef,3",
            "Reef Auto Missed": "autoReefMiss,0",
            "Reef Tele-Op": "teleReef,0",
            "Reef Tele-Op L1": "teleReef,0",
            "Reef Tele-Op L2": "teleReef,1",
            "Reef Tele-Op L3": "teleReef,2",
            "Reef Tele-Op L4": "teleReef,3",
            "Reef Tele-Op Missed": "teleReefMiss,0",
            "Processor Auto": "autoProcessor,0",
            "Processor Auto Missed": "autoProcessorMiss,0",
            "Processor Tele-Op": "teleProcessor,0",
            "Processor Tele-Op Missed": "teleProcessorMiss,0",
            "Net Auto": "autoNet,0",
            "Net Auto Missed": "autoNetMiss,0",
            "Net Tele-Op": "teleNet,0",
            "Net Tele-Op Missed": "teleNetMiss,0",
            "Ending Position": "endPos,0",
            "Attempted Ending Position": "attemptedEndPos,0",
            "Minor Fouls": "minorFouls,0",
            "Major Fouls": "majorFouls,0",
        }
        self.teamTableDisplayNames = {
            "score": "Score Impact",
            "autoLeave": "Auto Leave",
            "autoReefL1": "Reef Auto L1",
            "autoReefL2": "Reef Auto L2",
            "autoReefL3": "Reef Auto L3",
            "autoReefL4": "Reef Auto L4",
            "autoReefMiss": "Reef Auto Missed",
            "autoReefTotal": "Reef Auto Total",
            "teleReefL1": "Reef Tele-Op L1",
            "teleReefL2": "Reef Tele-Op L2",
            "teleReefL3": "Reef Tele-Op L3",
            "teleReefL4": "Reef Tele-Op L4",
            "teleReefMiss": "Reef Tele-Op Missed",
            "teleReefTotal": "Reef Tele-Op Total",
            "autoProcessor": "Processor Auto",
            "autoProcessorMiss": "Processor Auto Missed",
            "teleProcessor": "Processor Tele-Op",
            "teleProcessorMiss": "Processor Tele-Op Missed",
            "autoNet": "Net Auto",
            "autoNetMiss": "Net Auto Missed",
            "teleNet": "Net Tele-Op",
            "teleNetMiss": "Net Tele-Op Missed",
            "minorFouls": "Minor Fouls",
            "majorFouls": "Major Fouls",
        }
        self.matchTableDisplayNames = {
            "team": "Team",
            "displayName": "Display Name",
            "score": "Score Impact",
            "matchNumber": "Match Number",
            "setNumber": "Set Number",
            "compLevel": "Competition Level",
            "startPos": "Starting Position",
            "autoLeave": "Auto Leave",
            "autoReefL1": "Reef Auto L1",
            "autoReefL2": "Reef Auto L2",
            "autoReefL3": "Reef Auto L3",
            "autoReefL4": "Reef Auto L4",
            "autoReefMiss": "Reef Auto Missed",
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
            "attemptedEndPos": "Attempted Ending Position",
            "endPosSuccess": "Ending Position Sucecss",
            "minorFouls": "Minor Fouls",
            "majorFouls": "Major Fouls",
            "comment": "Comment",
        }
        self.cannedComments = [
            "Good Driving",
            "Bad Driving",
            "Fast Driving",
            "Slow Driving",
            "Removed Algae",
            "Coral Station During Auto",
            "Played Defense",
            "Good Defense",
            "Bad Defense",
            "Was Defended",
            "Multiple Fouls",
            "Multiple Jams",
            "Bumpers Off",
            "Tipped/Stuck",
            "Died",
            "No Show",
            "Bad Descision Making",
        ]
        self.pitScoutAutoCapabilities = tuple()
        self.pitScoutTeleCapabilities = tuple()

    def calculateScore(
        self,
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
    ) -> int:
        """
        Calculate the total score from scouted values.

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
            if endPos == EndPositionReefscape.PARK.value
            else (
                6
                if endPos == EndPositionReefscape.SHALLOW.value
                else 12 if endPos == EndPositionReefscape.DEEP.value else 0
            )
        )

        score -= 2 * minorFouls
        score -= 6 * majorFouls

        return score

    def scoreRobotInMatch(
        self,
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
        attemptedEndPos: EndPositionReefscape,
        minorFouls: int,
        majorFouls: int,
        comment: str,
        cannedComments: List[str],
        scout: str,
    ) -> bool:
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
                        "autoReefTotal": autoReef[0]
                        + autoReef[1]
                        + autoReef[2]
                        + autoReef[3],
                        "teleReef": teleReef,
                        "teleReefMiss": teleReefMiss,
                        "teleReefTotal": teleReef[0]
                        + teleReef[1]
                        + teleReef[2]
                        + teleReef[3],
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
                        "score": self.calculateScore(
                            autoLeave,
                            autoReef,
                            teleReef,
                            autoProcessor,
                            teleProcessor,
                            autoNet,
                            teleNet,
                            (
                                attemptedEndPos.value
                                if endPosSuccess
                                else EndPositionReefscape.NONE.value
                            ),
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

    def calculateScoreFromData(
        self, matchData: dict, team: Station, edit: int = -1
    ) -> int:
        """
        Gets a robot's result from the database and scores it.

        Inputs:
        - matchData (dict): a match dict
        - team (Station): the station to score
        - edit (int): which revision to score, defaults to the latest

        Returns:
        - int: calculated score
        """
        results = matchData["results"][team.value][edit]
        score = self.calculateScore(
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

    def calculateAverageAllianceScore(
        self, team1: int, team2: int, team3: int, calc=getMeanOfScoringCategory
    ):
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

        autoReef[0] += (
            (max(autoReef[1], 12) - 12)
            + (max(autoReef[2], 12) - 12)
            + (max(autoReef[3], 12) - 12)
        )

        autoReef = [
            autoReef[0],
            min(autoReef[1], 12),
            min(autoReef[2], 12),
            min(autoReef[3], 12),
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
            min(teleReefValues[1], 12 - autoReef[1]),
            min(teleReefValues[1], 12 - autoReef[1]),
            min(teleReefValues[1], 12 - autoReef[1]),
        ]
        teleReef[0] += (
            max(0, teleReefValues[1] - teleReef[1])
            + max(0, teleReefValues[2] - teleReef[2])
            + max(0, teleReefValues[3] - teleReef[3])
        )

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

        score = self.calculateScore(
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
            if team1End == EndPositionReefscape.PARK.value
            else (
                6
                if team1End == EndPositionReefscape.SHALLOW.value
                else 12 if team1End == EndPositionReefscape.DEEP.value else 0
            )
        )
        score += (
            2
            if team2End == EndPositionReefscape.PARK.value
            else (
                6
                if team2End == EndPositionReefscape.SHALLOW.value
                else 12 if team2End == EndPositionReefscape.DEEP.value else 0
            )
        )
        score += (
            2
            if team3End == EndPositionReefscape.PARK.value
            else (
                6
                if team3End == EndPositionReefscape.SHALLOW.value
                else 12 if team3End == EndPositionReefscape.DEEP.value else 0
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
        self, team1: int, team2: int, team3: int, maximum: bool = True
    ):
        """
        Calculates a hypothetical alliance score of three teams using their minimum or maximum results in each category.

        Inputs:
        - team1 (int): team number 1
        - team2 (int): team number 2
        - team3 (int): team number 3
        - maximum (bool): True uses maximum, False uses minimum, defaults to True

        Returns:
        - dict or none: dict of predicted results, or None if any teams are not found.
        """
        statistic = getMatchWithHighestValue if maximum else getMatchWithLowestValue
        oppositeStatistic = (
            getMatchWithLowestValue if maximum else getMatchWithHighestValue
        )

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

        autoReef[0] += (
            (max(autoReef[1], 12) - 12)
            + (max(autoReef[2], 12) - 12)
            + (max(autoReef[3], 12) - 12)
        )

        autoReef = [
            autoReef[0],
            min(autoReef[1], 12),
            min(autoReef[2], 12),
            min(autoReef[3], 12),
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
            min(teleReefValues[1], 12 - autoReef[1]),
            min(teleReefValues[1], 12 - autoReef[1]),
            min(teleReefValues[1], 12 - autoReef[1]),
        ]
        teleReef[0] += (
            max(0, teleReefValues[1] - teleReef[1])
            + max(0, teleReefValues[2] - teleReef[2])
            + max(0, teleReefValues[3] - teleReef[3])
        )

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

        score = self.calculateScore(
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
            if team1End == EndPositionReefscape.PARK.value
            else (
                6
                if team1End == EndPositionReefscape.SHALLOW.value
                else 12 if team1End == EndPositionReefscape.DEEP.value else 0
            )
        )
        score += (
            2
            if team2End == EndPositionReefscape.PARK.value
            else (
                6
                if team2End == EndPositionReefscape.SHALLOW.value
                else 12 if team2End == EndPositionReefscape.DEEP.value else 0
            )
        )
        score += (
            2
            if team3End == EndPositionReefscape.PARK.value
            else (
                6
                if team3End == EndPositionReefscape.SHALLOW.value
                else 12 if team3End == EndPositionReefscape.DEEP.value else 0
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

    def getAllStats(self, team: int) -> dict:
        """
        Calculates all stats for every single scoring category.

        Inputs:
        - team (int): Team number

        Returns:
        - dict: dict of every scoring category with every stat
        """
        teamResults = getTeamResults(team)
        return {
            "startPos": getAllStatsForCategory(teamResults, "startPos"),
            "autoLeave": getAllStatsForCategory(teamResults, "autoLeave"),
            "autoReefL1": getAllStatsForCategory(teamResults, "autoReef", 0),
            "autoReefL2": getAllStatsForCategory(teamResults, "autoReef", 1),
            "autoReefL3": getAllStatsForCategory(teamResults, "autoReef", 2),
            "autoReefL4": getAllStatsForCategory(teamResults, "autoReef", 3),
            "autoReefMiss": getAllStatsForCategory(teamResults, "autoReefMiss"),
            "teleReefL1": getAllStatsForCategory(teamResults, "teleReef", 0),
            "teleReefL2": getAllStatsForCategory(teamResults, "teleReef", 1),
            "teleReefL3": getAllStatsForCategory(teamResults, "teleReef", 2),
            "teleReefL4": getAllStatsForCategory(teamResults, "teleReef", 3),
            "teleReefMiss": getAllStatsForCategory(teamResults, "teleReefMiss"),
            "autoProcessor": getAllStatsForCategory(teamResults, "autoProcessor"),
            "autoProcessorMiss": getAllStatsForCategory(
                teamResults, "autoProcessorMiss"
            ),
            "teleProcessor": getAllStatsForCategory(teamResults, "teleProcessor"),
            "teleProcessorMiss": getAllStatsForCategory(
                teamResults, "teleProcessorMiss"
            ),
            "autoNet": getAllStatsForCategory(teamResults, "autoNet"),
            "autoNetMiss": getAllStatsForCategory(teamResults, "autoNetMiss"),
            "teleNet": getAllStatsForCategory(teamResults, "teleNet"),
            "teleNetMiss": getAllStatsForCategory(teamResults, "teleNetMiss"),
            "endPosSuccess": getAllStatsForCategory(teamResults, "endPosSuccess"),
            "attemptedEndPos": getAllStatsForCategory(teamResults, "attemptedEndPos"),
            "minorFouls": getAllStatsForCategory(teamResults, "minorFouls"),
            "majorFouls": getAllStatsForCategory(teamResults, "majorFouls"),
            "score": getAllStatsForCategory(teamResults, "score"),
        }


class Rebuilt(Game):
    def __init__(self, matches: Collection, teams: Collection):
        self.keyDisplayNames = {
            "matchNumber": "Match Number",
            "setNumber": "Set Number",
            "compLevel": "Competition Level",
            "preloadFuel": "Preloaded Fuel",
            "autoFuel": "Auto Fuel",
            "autoFuelTotal": "Total Auto Fuel",
            "autoFuelTotalMissed": "Total Auto Fuel Missed",
            "autoDepot": "Intaked from Depot During Auto",
            "autoBump": "Went over the Bump in Auto",
            "autoTrench": "Went under the Trench in Auto",
            "autoNeutralIntake": "Intaked from the Neutral Zone during Auto",
            "autoAttemptedSecondScore": "Attempted to score past preloads during Auto",
            "autoSucceededSecondScore": "Succeeded to score past preloads during Auto",
            "autoClimbAttempted": "Auto L1 Climb Attempted",
            "autoClimbSuccess": "Auto L1 Climb Succeeded",
            "autoOutpostFeed": "Fed from the Outpost during Auto",
            "autoFedToOutpost": "Fed to the Outpost duringn Auto",
            "firstShift": "Active in first and third shifts",
            "transitionFuel": "Transition Shift Fuel",
            "transitionFuelTotal": "Total Transition Shift Fuel",
            "transitionFuelTotalMissed": "Total Transition Shift Fuel Missed",
            "transitionFed": "Fed Fuel Into Alliance Zone During Transition Period",
            "transitionDefense": "Defended During Transition Period",
            "firstActiveShiftFuel": "First Active Shift Fuel",
            "firstActiveShiftFuelTotal": "Total First Active Shift Fuel",
            "firstActiveShiftFuelTotalMissed": "Total First Active Shift Fuel Missed",
            "firstActiveShiftFed": "Fed Fuel Into Alliance Zone During the First Active Shift",
            "firstActiveShiftDefense": "Defended During the First Active Shift",
            "secondActiveShiftFuel": "Second Active Shift Fuel",
            "secondActiveShiftFuelTotal": "Total Second Active Shift Fuel",
            "secondActiveShiftFuelTotalMissed": "Total Second Active Shift Fuel Missed",
            "secondActiveShiftFed": "Fed Fuel Into Alliance Zone During the Second Active Shift",
            "secondActiveShiftDefense": "Defended During the Second Active Shift",
            "firstInactiveShiftScored": "Scored During First Inactive Shift",
            "firstInactiveShiftFed": "Fed Fuel Into Alliance Zone During First Inactive Shift",
            "firstInactiveShiftDefense": "Defended During First Inactive Shift",
            "secondInactiveShiftScored": "Scored During Second Inactive Shift",
            "secondInactiveShiftFed": "Fed Fuel Into Alliance Zone During Second Inactive Shift",
            "secondInactiveShiftDefense": "Defended During First Inactive Shift",
            "endgameFuel": "Endgame Fuel",
            "endgameFuelTotal": "Total Endgame Fuel",
            "endgameFuelTotalMissed": "Total Endgame Fuel Missed",
            "endgameFed": "Fed Fuel Into Alliance Zone During Endgame",
            "endgameDefense": "Defended During Endgame",
            "endClimb": "Endgame Climb",
            "endClimbAttempted": "Endgame Climb Attempted",
            "outpostIntake": "Intaked from the Outpost",
            "groundIntake": "Intaked from the ground",
            "fedToOutpost": "Fed to the outpost",
            "totalFuel": "Total Fuel Worth Points",
            "totalFuelMissed": "Total Fuel Missed",
            "minorFouls": "Minor Fouls",
            "majorFouls": "Major Fouls",
            "score": "Score Impact",
            "comment": "Comment",
            "cannedComments": "Canned Comments",
            "scout": "Scout",
            "autoFuelAverageShotPerSecond": "Average Auto Fuel Shot Per Second",
            "autoFuelAverageScoredPerSecond": "Average Auto Fuel Scored Per Second",
            "transitionFuelAverageShotPerSecond": "Average Transition Fuel Shot Per Second",
            "transitionFuelAverageScoredPerSecond": "Average Transition Fuel Scored Per Second",
            "firstActiveShiftFuelAverageShotPerSecond": "Average First Active Shift Fuel Shot Per Second",
            "firstActiveShiftFuelAverageScoredPerSecond": "Average First Active Shift Fuel Scored Per Second",
            "secondActiveShiftFuelAverageShotPerSecond": "Average Second Active Shift Fuel Shot Per Second",
            "secondActiveShiftFuelAverageScoredPerSecond": "Average Second Active Shift Fuel Scored Per Second",
            "endgameFuelAverageShotPerSecond": "Average Endgame Fuel Shot Per Second",
            "endgameFuelAverageScoredPerSecond": "Average Endgame Fuel Scored Per Second",
            "totalFuelAverageShotPerSecond": "Average Fuel Shot Per Second",
            "totalFuelAverageScoredPerSecond": "Average Fuel Scored Per Second",
        }
        self.matches = matches
        self.teams = teams
        self.teamRankOptions = {
            "Score Impact": "score,0",
            "Preloaded Fuel": "preloadFuel,0",
            "Auto Fuel Total": "autoFuelTotal,0",  # fuel is special :3
            "Auto Fuel Missed": "autoFuelMissed,0",
            "Intaked from Depot during Auto": "autoDepot,0",
            "Went over the Bump in Auto": "autoBump,0",
            "Went under the Trench in Auto": "autoTrench,0",
            "Intaked from the Neutral Zone during Auto": "autoNeutralIntake,0",
            "Attempted to score past preloads during Auto": "autoAttemptedSecondScore,0",
            "Succeeded to score past preloads during Auto": "autoSucceededSecondScore,0",
            "Auto L1 Climb Attempted": "autoClimbAttempted,0",
            "Auto L1 Climb Succeeded": "autoClimbSuccess,0",
            "Active in first and third shifts": "firstShift,0",
            # teleop fuel block
            "Transition Shift Fuel Total": "transitionFuelTotal,0",
            "Transition Shift Fuel Missed": "transitionFuelTotalMissed,0",
            "First Active Shift Fuel Total": "firstActiveShiftFuelTotal,0",
            "Second Active Shift Fuel Total": "secondActiveShiftFuelTotal,0",
            "Endgame Fuel Total": "endgameFuelTotal,0",
            "First Active Shift Fuel Missed": "firstActiveShiftFuelMissed,0",
            "Second Active Shift Fuel Missed": "secondActiveShiftFuelMissed,0",
            "Endgame Fuel Missed": "endgameFuelMissed,0",
            "Scored During First Inactive Shift": "scoredDuringFirstInactiveShift,0",
            "Scored During Second Inactive Shift": "scoredDuringSecondInactiveShift,0",
            "Endgame Climb": "endClimb,0",
            "Endgame Climb Attempted": "endClimbAttempted,0",
            "Played Defense": "playedDefense,0",
            "Fed to Alliance Zone during Active Shift": "fedToAllianceActive,0",
            "Fed to Alliance Zone during Inactive Shift": "fedToAllianceInactive,0",
            "Intaked from the Outpost": "outpostIntake,0",
            "Intaked from the ground": "groundIntake,0",
            "Total Fuel Worth Points": "totalFuel,0",
            "Total Fuel Missed": "totalFuelMissed,0",
            "Minor Fouls": "minorFouls,0",
            "Major Fouls": "majorFouls,0",
            "Average Auto Fuel Shot Per Second": "autoFuelAverageShotPerSecond,0",
            "Average Auto Fuel Scored Per Second": "autoFuelAverageScoredPerSecond,0",
            "Average Transition Fuel Shot Per Second": "transitionFuelAverageShotPerSecond,0",
            "Average Transition Fuel Scored Per Second": "transitionFuelAverageScoredPerSecond,0",
            "Average First Active Shift Fuel Shot Per Second": "firstActiveShiftFuelAverageShotPerSecond,0",
            "Average First Active Shift Fuel Scored Per Second": "firstActiveShiftFuelAverageScoredPerSecond,0",
            "Average Second Active Shift Fuel Shot Per Second": "secondActiveShiftFuelAverageShotPerSecond,0",
            "Average Second Active Shift Fuel Scored Per Second": "secondActiveShiftFuelAverageScoredPerSecond,0",
            "Average Endgame Fuel Shot Per Second": "endgameFuelAverageShotPerSecond,0",
            "Average Endgame Fuel Scored Per Second": "endgameFuelAverageScoredPerSecond,0",
            "Average Fuel Shot Per Second": "totalFuelAverageShotPerSecond,0",
            "Average Fuel Scored Per Second": "totalFuelAverageScoredPerSecond,0",
        }
        self.teamTableDisplayNames = {
            "score": "Score Impact",
            "preloadFuel": "Preloaded Fuel",
            "autoFuelTotal": "Total Auto Fuel",
            "autoFuelTotalMissed": "Total Auto Fuel Missed",
            "autoDepot": "Intaked from Depot During Auto",
            "autoBump": "Went over the Bump in Auto",
            "autoTrench": "Went under the Trench in Auto",
            "autoNeutralIntake": "Intaked from the Neutral Zone during Auto",
            "autoAttemptedSecondScore": "Attempted to score past preloads during Auto",
            "autoSucceededSecondScore": "Succeeded to score past preloads during Auto",
            "autoClimbAttempted": "Auto L1 Climb Attempted",
            "autoClimbSuccess": "Auto L1 Climb Succeeded",
            "autoOutpostFeed": "Fed from the Outpost during Auto",
            "autoFedToOutpost": "Fed to the Outpost duringn Auto",
            "firstShift": "Active in first and third shifts",
            "transitionFuelTotal": "Total Transition Shift Fuel",
            "transitionFuelTotalMissed": "Total Transition Shift Fuel Missed",
            "firstActiveShiftFuelTotal": "Total First Active Shift Fuel",
            "firstActiveShiftFuelTotalMissed": "Total First Active Shift Fuel Missed",
            "secondActiveShiftFuelTotal": "Total Second Active Shift Fuel",
            "secondActiveShiftFuelTotalMissed": "Total Second Active Shift Fuel Missed",
            "scoredDuringFirstInactiveShift": "Scored During First Inactive Shift",
            "scoredDuringSecondInactiveShift": "Scored During Second Inactive Shift",
            "endgameFuelTotal": "Total Endgame Fuel",
            "endgameFuelTotalMissed": "Total Endgame Fuel Missed",
            "endClimb": "Endgame Climb",
            "endClimbAttempted": "Endgame Climb Attempted",
            "playedDefense": "Played Defense",
            "fedToAllianceActive": "Fed to Alliance Zone during Active Shift",
            "fedToAllianceInactive": "Fed to Alliance Zone during Inactive Shift",
            "outpostIntake": "Intaked from the Outpost",
            "groundIntake": "Intaked from the ground",
            "totalFuel": "Total Fuel Worth Points",
            "totalFuelMissed": "Total Fuel Missed",
            "minorFouls": "Minor Fouls",
            "majorFouls": "Major Fouls",
            "autoFuelAverageShotPerSecond": "Average Auto Fuel Shot Per Second",
            "autoFuelAverageScoredPerSecond": "Average Auto Fuel Scored Per Second",
            "transitionFuelAverageShotPerSecond": "Average Transition Fuel Shot Per Second",
            "transitionFuelAverageScoredPerSecond": "Average Transition Fuel Scored Per Second",
            "firstActiveShiftFuelAverageShotPerSecond": "Average First Active Shift Fuel Shot Per Second",
            "firstActiveShiftFuelAverageScoredPerSecond": "Average First Active Shift Fuel Scored Per Second",
            "secondActiveShiftFuelAverageShotPerSecond": "Average Second Active Shift Fuel Shot Per Second",
            "secondActiveShiftFuelAverageScoredPerSecond": "Average Second Active Shift Fuel Scored Per Second",
            "endgameFuelAverageShotPerSecond": "Average Endgame Fuel Shot Per Second",
            "endgameFuelAverageScoredPerSecond": "Average Endgame Fuel Scored Per Second",
            "totalFuelAverageShotPerSecond": "Average Fuel Shot Per Second",
            "totalFuelAverageScoredPerSecond": "Average Fuel Scored Per Second",
        }
        self.matchTableDisplayNames = {
            "team": "Team",
            "displayName": "Display Name",
            "score": "Score Impact",
            "matchNumber": "Match Number",
            "setNumber": "Set Number",
            "compLevel": "Competition Level",
            "startPos": "Starting Position",
            "preloadFuel": "Preloaded Fuel",
            # "autoFuel": "Auto Fuel",
            "autoFuelTotal": "Total Auto Fuel",
            "autoFuelTotalMissed": "Total Auto Fuel Missed",
            "autoFuelAverageShotPerSecond": "Average Auto Fuel Shot Per Second",
            "autoFuelAverageScoredPerSecond": "Average Auto Fuel Scored Per Second",
            "autoDepot": "Intaked from Depot During Auto",
            "autoBump": "Went over the Bump in Auto",
            "autoTrench": "Went under the Trench in Auto",
            "autoNeutralIntake": "Intaked from the Neutral Zone during Auto",
            "autoAttemptedSecondScore": "Attempted to score past preloads during Auto",
            "autoSucceededSecondScore": "Succeeded to score past preloads during Auto",
            "autoClimbAttempted": "Auto L1 Climb Attempted",
            "autoClimbSuccess": "Auto L1 Climb Succeeded",
            "autoOutpostFeed": "Fed from the Outpost during Auto",
            "autoFedToOutpost": "Fed to the Outpost duringn Auto",
            "firstShift": "Active in first and third shifts",
            # "transitionFuel": "Transition Shift Fuel",
            "transitionFuelTotal": "Total Transition Shift Fuel",
            "transitionFuelTotalMissed": "Total Transition Shift Fuel Missed",
            "transitionFuelAverageShotPerSecond": "Average Transition Fuel Shot Per Second",
            "transitionFuelAverageScoredPerSecond": "Average Transition Fuel Scored Per Second",
            # "firstActiveShiftFuel": "First Active Shift Fuel",
            "firstActiveShiftFuelTotal": "Total First Active Shift Fuel",
            "firstActiveShiftFuelTotalMissed": "Total First Active Shift Fuel Missed",
            "firstActiveShiftFuelAverageShotPerSecond": "Average First Active Shift Fuel Shot Per Second",
            "firstActiveShiftFuelAverageScoredPerSecond": "Average First Active Shift Fuel Scored Per Second",
            # "secondActiveShiftFuel": "Second Active Shift Fuel",
            "secondActiveShiftFuelTotal": "Total Second Active Shift Fuel",
            "secondActiveShiftFuelTotalMissed": "Total Second Active Shift Fuel Missed",
            "secondActiveShiftFuelAverageShotPerSecond": "Average Second Active Shift Fuel Shot Per Second",
            "secondActiveShiftFuelAverageScoredPerSecond": "Average Second Active Shift Fuel Scored Per Second",
            "firstInactiveShiftScored": "Scored During First Inactive Shift",
            "secondInactiveShiftScored": "Scored During Second Inactive Shift",
            # "endgameFuel": "Endgame Fuel",
            "endgameFuelTotal": "Total Endgame Fuel",
            "endgameFuelTotalMissed": "Total Endgame Fuel Missed",
            "endgameFuelAverageShotPerSecond": "Average Endgame Fuel Shot Per Second",
            "endgameFuelAverageScoredPerSecond": "Average Endgame Fuel Scored Per Second",
            "endClimb": "Endgame Climb",
            "endClimbAttempted": "Endgame Climb Attempted",
            # "playedDefense": "Played Defense",
            # "fedToAllianceActive": "Fed to Alliance Zone during Active Shift",
            # "fedToAllianceInactive": "Fed to Alliance Zone during Inactive Shift",
            "outpostIntake": "Intaked from the Outpost",
            "groundIntake": "Intaked from the ground",
            "totalFuel": "Total Fuel Worth Points",
            "totalFuelMissed": "Total Fuel Missed",
            "totalFuelAverageShotPerSecond": "Average Fuel Shot Per Second",
            "totalFuelAverageScoredPerSecond": "Average Fuel Scored Per Second",
            "minorFouls": "Minor Fouls",
            "majorFouls": "Major Fouls",
            "comment": "Comment",
            "cannedComments": "Canned Comments",
            "scout": "Scout",
        }
        self.cannedComments = [
            "Good Driving",
            "Bad Driving",
            "Fast Driving",
            "Slow Driving",
            "Played Defense",
            "Good Defense",
            "Bad Defense",
            "Was Defended",
            "Multiple Fouls",
            "Multiple Jams",
            "Bumpers Off",
            "Tipped/Stuck",
            "Died",
            "No Show",
            "Bad Descision Making",
        ]
        self.pitScoutAutoCapabilities = (
            ("Score in hub", "auto-fuel"),
            ("Intake from depot", "auto-depot"),
            ("Intake from outpost chute", "auto-outpost"),
            ("Intake from neutral zone", "auto-neutral"),
            ("Climb level 1 in the center", "auto-climb1-center"),
            ("Climb level 1 on the sides", "auto-climb1-side"),
            ("Climb level 1 in the inside", "auto-climb1-inside"),
        )
        self.pitScoutTeleCapabilities = (
            ("Score in hub", "tele-fuel"),
            ("Intake from depot", "tele-depot"),
            ("Intake from outpost chute", "tele-outpost"),
            ("Intake from neutral zone", "tele-neutral"),
            ("Climb level 1 in the center", "tele-climb1-center"),
            ("Climb level 1 on the sides", "tele-climb1-side"),
            ("Climb level 1 in the inside", "tele-climb1-inside"),
            ("Climb level 2 in the center", "tele-climb2-center"),
            ("Climb level 2 on the sides", "tele-climb2-side"),
            ("Climb level 2 in the inside", "tele-climb2-inside"),
            ("Climb level 3 in the center", "tele-climb3-center"),
            ("Climb level 3 on the sides", "tele-climb3-side"),
            ("Climb level 3 in the inside", "tele-climb3-inside"),
        )

    def calculateScore(
        self,
        fuel: int,
        autoClimb: bool,
        endClimb: EndPositionRebuilt,
        minorFouls: int,
        majorFouls: int,
    ) -> int:
        """
        Calculate the total score from scouted values.

        Inputs:
        - Self explanatory

        Outputs:
        - int: total score, minus points from fouls

        """
        score = 0
        score += int(fuel)
        if autoClimb:
            score += 15
        match endClimb:
            case EndPositionRebuilt.L1:
                score += 10
            case EndPositionRebuilt.L2:
                score += 20
            case EndPositionRebuilt.L3:
                score += 30

        score -= 5 * int(minorFouls)
        score -= 15 * int(majorFouls)
        return score

    def scoreRobotInMatch(
        self,
        matchNumber: int,
        setNumber: int,
        compLevel: CompLevel,
        station: Station,
        startPos: float,
        preloadFuel: int,
        autoFuel: list[dict],
        autoDepot: bool,
        autoBump: bool,
        autoTrench: bool,
        autoNeutralIntake: bool,
        autoAttemptedSecondScore: bool,
        autoSucceededSecondScore: bool,
        autoClimbAttempted: bool,
        autoClimbSuccess: bool,
        autoOutpostFeed: bool,
        autoFedToOutpost: bool,
        firstShift: bool,
        transitionFuel: list[dict],
        transitionFed: bool,
        transitionDefense: bool,
        firstActiveShiftFuel: list[dict],
        firstActiveShiftFed: bool,
        firstActiveShiftDefense: bool,
        secondActiveShiftFuel: list[dict],
        secondActiveShiftFed: bool,
        secondActiveShiftDefense: bool,
        firstInactiveShiftScored: bool,
        firstInactiveShiftFed: bool,
        firstInactiveShiftDefense: bool,
        secondInactiveShiftScored: bool,
        secondInactiveShiftFed: bool,
        secondInactiveShiftDefense: bool,
        endgameFuel: list[dict],
        endgameFed: bool,
        endgameDefense: bool,
        endClimb: EndPositionRebuilt,
        endClimbAttempted: EndPositionRebuilt,
        # playedDefense: bool,
        # fedToAllianceActive: bool,
        # fedToAllianceInactive: bool,
        outpostIntake: bool,
        groundIntake: bool,
        fedToOutpost: bool,
        minorFouls: int,
        majorFouls: int,
        comment: str,
        cannedComments: List[str],
        scout: str,
    ) -> bool:
        """
        Scores one robot in a match.

        Should change every year.

        Inputs:
        - self explanitory

        Returns:
        - Boolean: if the robot was successfully scored
        """
        totalFuel: int = 0
        totalFuelMissed: int = 0
        autoFuelTotal = 0
        autoFuelTotalMissed = 0
        transitionFuelTotal = 0
        transitionFuelTotalMissed = 0
        firstActiveShiftFuelTotal = 0
        firstActiveShiftFuelTotalMissed = 0
        secondActiveShiftFuelTotal = 0
        secondActiveShiftFuelTotalMissed = 0
        endgameFuelTotal = 0
        endgameFuelTotalMissed = 0

        for period in autoFuel:
            autoFuelTotal += period["scored"]
            autoFuelTotalMissed += period["missed"]
        for period in transitionFuel:
            transitionFuelTotal += period["scored"]
            transitionFuelTotalMissed += period["missed"]
        for period in firstActiveShiftFuel:
            firstActiveShiftFuelTotal += period["scored"]
            firstActiveShiftFuelTotalMissed += period["missed"]
        for period in secondActiveShiftFuel:
            secondActiveShiftFuelTotal += period["scored"]
            secondActiveShiftFuelTotalMissed += period["missed"]
        for period in endgameFuel:
            endgameFuelTotal += period["scored"]
            endgameFuelTotalMissed += period["missed"]
        totalFuel = (
            autoFuelTotal
            + transitionFuelTotal
            + firstActiveShiftFuelTotal
            + secondActiveShiftFuelTotal
            + endgameFuelTotal
        )
        totalFuelMissed = (
            autoFuelTotalMissed
            + transitionFuelTotalMissed
            + firstActiveShiftFuelTotalMissed
            + secondActiveShiftFuelTotalMissed
            + endgameFuelTotalMissed
        )
        data = {
            "startPos": startPos,
            "preloadFuel": preloadFuel,
            "autoFuel": autoFuel,
            "autoFuelTotal": autoFuelTotal,
            "autoFuelTotalMissed": autoFuelTotalMissed,
            "autoDepot": autoDepot,
            "autoBump": autoBump,
            "autoTrench": autoTrench,
            "autoNeutralIntake": autoNeutralIntake,
            "autoAttemptedSecondScore": autoAttemptedSecondScore,
            "autoSucceededSecondScore": autoSucceededSecondScore,
            "autoClimbAttempted": autoClimbAttempted,
            "autoClimbSuccess": autoClimbSuccess,
            "autoOutpostFeed": autoOutpostFeed,
            "autoFedToOutpost": autoFedToOutpost,
            "firstShift": firstShift,
            "transitionFuel": transitionFuel,
            "transitionFuelTotal": transitionFuelTotal,
            "transitionFuelTotalMissed": transitionFuelTotalMissed,
            "transitionFed": transitionFed,
            "transitionDefense": transitionDefense,
            "firstActiveShiftFuel": firstActiveShiftFuel,
            "firstActiveShiftFuelTotal": firstActiveShiftFuelTotal,
            "firstActiveShiftFed": firstActiveShiftFed,
            "firstActiveShiftDefense": firstActiveShiftDefense,
            "firstActiveShiftFuelTotalMissed": firstActiveShiftFuelTotalMissed,
            "secondActiveShiftFuel": secondActiveShiftFuel,
            "secondActiveShiftFuelTotal": secondActiveShiftFuelTotal,
            "secondActiveShiftFed": secondActiveShiftFed,
            "secondActiveShiftDefense": secondActiveShiftDefense,
            "secondActiveShiftFuelTotalMissed": secondActiveShiftFuelTotalMissed,
            "firstInactiveShiftScored": firstInactiveShiftScored,
            "firstInactiveShiftFed": firstInactiveShiftFed,
            "firstInactiveShiftDefense": firstInactiveShiftDefense,
            "secondInactiveShiftScored": secondInactiveShiftScored,
            "secondInactiveShiftFed": secondInactiveShiftFed,
            "secondInactiveShiftDefense": secondInactiveShiftDefense,
            "endgameFuel": endgameFuel,
            "endgameFuelTotal": endgameFuelTotal,
            "endgameFed": endgameFed,
            "endgameDefense": endgameDefense,
            "endgameFuelTotalMissed": endgameFuelTotalMissed,
            "endClimb": endClimb.value,
            "endClimbAttempted": endClimbAttempted.value,
            # "playedDefense": playedDefense,
            # "fedToAllianceActive": fedToAllianceActive,
            # "fedToAllianceInactive": fedToAllianceInactive,
            "outpostIntake": outpostIntake,
            "groundIntake": groundIntake,
            "fedToOutpost": fedToOutpost,
            "totalFuel": totalFuel,
            "totalFuelMissed": totalFuelMissed,
            "minorFouls": minorFouls,
            "majorFouls": majorFouls,
            "score": self.calculateScore(
                totalFuel, autoClimbSuccess, endClimb, minorFouls, majorFouls
            ),
            "comment": comment,
            "cannedComments": cannedComments,
            "scout": scout,
        }

        totalShotPerSecond = 0
        totalScoredPerSecond = 0
        totalDataLength = 0
        for period in (
            "autoFuel",
            "transitionFuel",
            "firstActiveShiftFuel",
            "secondActiveShiftFuel",
            "endgameFuel",
        ):
            periodShotPerSecond = 0
            periodScoredPerSecond = 0
            dataLength = len(data[period])
            for i in range(dataLength):
                try:
                    data[period][i]["fuelScoredPerSecond"] = (
                        data[period][i]["scored"] / data[period][i]["time"]
                    )
                except ZeroDivisionError:
                    data[period][i]["fuelScoredPerSecond"] = 0
                    app.logger.warning(f"NaN calculated for fuelScoredPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")
                try:
                    data[period][i]["fuelShotPerSecond"] = (
                        data[period][i]["scored"] + data[period][i]["missed"]
                    ) / data[period][i]["time"]
                except ZeroDivisionError:
                    data[period][i]["fuelShotPerSecond"] = 0
                    app.logger.warning(f"NaN calculated for fuelShotPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")

                periodShotPerSecond += data[period][i]["fuelShotPerSecond"]
                periodScoredPerSecond += data[period][i]["fuelScoredPerSecond"]
                totalShotPerSecond += data[period][i]["fuelShotPerSecond"]
                totalScoredPerSecond += data[period][i]["fuelScoredPerSecond"]

            totalDataLength += dataLength
            dataLength = 1 if dataLength <= 0 else dataLength

            try:
                data[f"{period}AverageShotPerSecond"] = periodShotPerSecond / dataLength
            except ZeroDivisionError:
                    data[f"{period}AverageShotPerSecond"] = 0
                    app.logger.warning(f"NaN calculated for {period}AverageShotPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")
            try:
                data[f"{period}AverageScoredPerSecond"] = periodScoredPerSecond / dataLength
            except ZeroDivisionError:
                data[f"{period}AverageScoredPerSecond"] = 0
                app.logger.warning(f"NaN calculated for {period}AverageScoredPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")

        try:
            data[f"totalFuelAverageShotPerSecond"] = totalShotPerSecond / totalDataLength
        except ZeroDivisionError:
            data[f"totalFuelAverageShotPerSecond"] = 0
            app.logger.warning(f"NaN calculated for totalFuelAverageShotPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")
        try:
            data[f"totalFuelAverageScoredPerSecond"] = (
                totalScoredPerSecond / totalDataLength
            )
        except ZeroDivisionError:
            data[f"totalFuelAverageScoredPerSecond"] = 0
            app.logger.warning(f"NaN calculated for totalFuelAverageScoredPerSecond {station.value} in {compLevel.value}{matchNumber}_{setNumber}")

        result = matches.update_many(
            {
                "matchNumber": matchNumber,
                "setNumber": setNumber,
                "compLevel": compLevel.value,
            },
            {"$push": {"results." + station.value: data}},
        )
        if result.matched_count == 0:
            app.logger.info(  # type: ignore
                f"Failed to score robot {station.value} for match {matchNumber} by {scout}: Match does not exist."
            )
            return False
        app.logger.info(f"Robot {station.value} scored for match {matchNumber} by {scout}.")  # type: ignore
        return True

    def calculateScoreFromData(
        self, matchData: dict, team: Station, edit: int = -1
    ) -> int:
        """
        Gets a robot's result from the database and scores it.

        Inputs:
        - matchData (dict): a match dict
        - team (Station): the station to score
        - edit (int): which revision to score, defaults to the latest

        Returns:
        - int: calculated score
        """
        results = matchData["results"][team.value][edit]
        if type(results["score"]) == int:
            return results["score"]
        else:
            app.logger.error(f"Request for score for {team.value} failed.")
            abort(400)

    def calculateAverageAllianceScore(
        self, team1: int, team2: int, team3: int, calc=getMeanOfScoringCategory
    ) -> dict | None:
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

        team1AutoClimb = int(calc(team1Data, "autoClimb") >= 0.5)
        team2AutoClimb = int(calc(team2Data, "autoClimb") >= 0.5)
        team3AutoClimb = int(calc(team3Data, "autoClimb") >= 0.5)
        autoClimbTotal = team1AutoClimb + team2AutoClimb + team3AutoClimb

        team1End = round(calc(team1Data, "endPos"))
        team2End = round(calc(team2Data, "endPos"))
        team3End = round(calc(team3Data, "endPos"))

        team1Minors = calc(team1Data, "minorFouls")
        team2Minors = calc(team2Data, "minorFouls")
        team3Minors = calc(team3Data, "minorFouls")

        team1Majors = calc(team1Data, "majorFouls")
        team2Majors = calc(team2Data, "majorFouls")
        team3Majors = calc(team3Data, "majorFouls")

        fuel = (
            round(calc(team1Data, "totalFuel"))
            + round(calc(team2Data, "totalFuel"))
            + round(calc(team3Data, "totalFuel"))
        )

        score = self.calculateScore(fuel, False, EndPositionRebuilt.NONE, 0, 0)

        score += autoClimbTotal * 15
        score += (
            10
            if team1End == EndPositionRebuilt.L1.value
            else (
                20
                if team1End == EndPositionRebuilt.L2.value
                else 30 if team1End == EndPositionRebuilt.L3.value else 0
            )
        )
        score += (
            10
            if team2End == EndPositionRebuilt.L1.value
            else (
                20
                if team2End == EndPositionRebuilt.L2.value
                else 30 if team2End == EndPositionRebuilt.L3.value else 0
            )
        )
        score += (
            10
            if team3End == EndPositionRebuilt.L1.value
            else (
                20
                if team3End == EndPositionRebuilt.L2.value
                else 30 if team3End == EndPositionRebuilt.L3.value else 0
            )
        )

        return {
            "score": score,
            "autoClimb": autoClimbTotal,
            "fuelTotal": fuel,
            "endPos1": team1End,
            "endPos2": team2End,
            "endPos3": team3End,
            "minorFouls": team1Minors + team2Minors + team3Minors,
            "majorFouls": team1Majors + team2Majors + team3Majors,
        }

    def calculateMinMaxAllianceScore(
        self, team1: int, team2: int, team3: int, maximum: bool = True
    ) -> dict | None:
        """
        Calculates a hypothetical alliance score of three teams using their minimum or maximum results in each category.

        Inputs:
        - team1 (int): team number 1
        - team2 (int): team number 2
        - team3 (int): team number 3
        - maximum (bool): True uses maximum, False uses minimum, defaults to True

        Returns:
        - dict or none: dict of predicted results, or None if any teams are not found.
        """
        statistic = getMatchWithHighestValue if maximum else getMatchWithLowestValue
        oppositeStatistic = (
            getMatchWithLowestValue if maximum else getMatchWithHighestValue
        )

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

        team1AutoClimb = int(statistic(team1Data, "autoClimb")["value"] >= 0.5)
        team2AutoClimb = int(statistic(team2Data, "autoClimb")["value"] >= 0.5)
        team3AutoClimb = int(statistic(team3Data, "autoClimb")["value"] >= 0.5)
        autoClimbTotal = team1AutoClimb + team2AutoClimb + team3AutoClimb

        team1End = round(statistic(team1Data, "endPos")["value"])
        team2End = round(statistic(team2Data, "endPos")["value"])
        team3End = round(statistic(team3Data, "endPos")["value"])

        team1Minors = statistic(team1Data, "minorFouls")["value"]
        team2Minors = statistic(team2Data, "minorFouls")["value"]
        team3Minors = statistic(team3Data, "minorFouls")["value"]

        team1Majors = statistic(team1Data, "majorFouls")["value"]
        team2Majors = statistic(team2Data, "majorFouls")["value"]
        team3Majors = statistic(team3Data, "majorFouls")["value"]

        fuel = (
            round(statistic(team1Data, "totalFuel")["value"])
            + round(statistic(team2Data, "totalFuel")["value"])
            + round(statistic(team3Data, "totalFuel")["value"])
        )

        score = self.calculateScore(fuel, False, EndPositionRebuilt.NONE, 0, 0)

        score += autoClimbTotal * 15
        score += (
            10
            if team1End == EndPositionRebuilt.L1.value
            else (
                20
                if team1End == EndPositionRebuilt.L2.value
                else 30 if team1End == EndPositionRebuilt.L3.value else 0
            )
        )
        score += (
            10
            if team2End == EndPositionRebuilt.L1.value
            else (
                20
                if team2End == EndPositionRebuilt.L2.value
                else 30 if team2End == EndPositionRebuilt.L3.value else 0
            )
        )
        score += (
            10
            if team3End == EndPositionRebuilt.L1.value
            else (
                20
                if team3End == EndPositionRebuilt.L2.value
                else 30 if team3End == EndPositionRebuilt.L3.value else 0
            )
        )

        return {
            "score": score,
            "autoClimb": autoClimbTotal,
            "fuelTotal": fuel,
            "endPos1": team1End,
            "endPos2": team2End,
            "endPos3": team3End,
            "minorFouls": team1Minors + team2Minors + team3Minors,
            "majorFouls": team1Majors + team2Majors + team3Majors,
        }

    def getAllStats(self, team: int) -> dict:
        """
        Calculates all stats for every single scoring category.

        Inputs:
        - team (int): Team number

        Returns:
        - dict: dict of every scoring category with every stat
        """
        teamResults = getTeamResults(team)
        return {
            "score": getAllStatsForCategory(teamResults, "score"),
            "preloadFuel": getAllStatsForCategory(teamResults, "preloadFuel"),
            "autoFuelTotal": getAllStatsForCategory(teamResults, "autoFuelTotal"),
            "autoFuelTotalMissed": getAllStatsForCategory(
                teamResults, "autoFuelTotalMissed"
            ),
            "autoFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "autoFuelAverageShotPerSecond"
            ),
            "autoFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "autoFuelAverageScoredPerSecond"
            ),
            "autoClimbAttempted": getAllStatsForCategory(
                teamResults, "autoClimbAttempted"
            ),
            "firstShift": getAllStatsForCategory(teamResults, "firstShift"),
            "transitionFuelTotal": getAllStatsForCategory(
                teamResults, "transitionFuelTotal"
            ),
            "transitionFuelTotalMissed": getAllStatsForCategory(
                teamResults, "transitionFuelTotalMissed"
            ),
            "transitionFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "transitionFuelAverageShotPerSecond"
            ),
            "transitionFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "transitionFuelAverageScoredPerSecond"
            ),
            "firstActiveShiftFuelTotal": getAllStatsForCategory(
                teamResults, "firstActiveShiftFuelTotal"
            ),
            "firstActiveShiftFuelTotalMissed": getAllStatsForCategory(
                teamResults, "firstActiveShiftFuelTotalMissed"
            ),
            "firstActiveShiftFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "firstActiveShiftFuelAverageShotPerSecond"
            ),
            "firstActiveShiftFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "firstActiveShiftFuelAverageScoredPerSecond"
            ),
            "secondActiveShiftFuelTotal": getAllStatsForCategory(
                teamResults, "secondActiveShiftFuelTotal"
            ),
            "secondActiveShiftFuelTotalMissed": getAllStatsForCategory(
                teamResults, "secondActiveShiftFuelTotalMissed"
            ),
            "secondActiveShiftFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "secondActiveShiftFuelAverageShotPerSecond"
            ),
            "secondActiveShiftFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "secondActiveShiftFuelAverageScoredPerSecond"
            ),
            "endgameFuelTotal": getAllStatsForCategory(teamResults, "endgameFuelTotal"),
            "endgameFuelTotalMissed": getAllStatsForCategory(
                teamResults, "endgameFuelTotalMissed"
            ),
            "endgameFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "endgameFuelAverageShotPerSecond"
            ),
            "endgameFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "endgameFuelAverageScoredPerSecond"
            ),
            "endClimb": getAllStatsForCategory(teamResults, "endClimb"),
            "endClimbAttempted": getAllStatsForCategory(teamResults, "endClimbAttempted"),
            "totalFuel": getAllStatsForCategory(teamResults, "totalFuel"),
            "totalFuelAverageShotPerSecond": getAllStatsForCategory(
                teamResults, "totalFuelAverageShotPerSecond"
            ),
            "totalFuelAverageScoredPerSecond": getAllStatsForCategory(
                teamResults, "totalFuelAverageScoredPerSecond"
            ),
            "minorFouls": getAllStatsForCategory(teamResults, "minorFouls"),
            "majorFouls": getAllStatsForCategory(teamResults, "majorFouls"),
        }

    def calculateAllianceFromMatches(
        self,
        team1: int,
        match1: list,
        team2: int,
        match2: list,
        team3: int,
        match3: list,
        jsonSerializable: bool = False,
    ) -> dict:
        """
        Adds together results for three teams from given match data to predict their performance as an alliance.

        Inputs:
        - team1 (int): team 1 number
        - match1 (list): match data for team 1
        - team2 (int): team 2 number
        - match2 (list): match data for team 2
        - team3 (int): team 3 number
        - match3 (list): match data for team 3
        - jsonSerializable (bool): if True, converts EndPositionRebuilt objects in endgameClimbs to int. defaults to False.

        Returns:
        - dict: predicted results dict
        """
        team1Station = None
        for station, team in match1[0]["teams"].items():
            if team == team1:
                team1Station = Station(station)
        if not team1Station:
            return {}
        team2Station = None
        for station, team in match2[0]["teams"].items():
            if team == team2:
                team2Station = Station(station)
        if not team2Station:
            return {}
        team3Station = None
        for station, team in match3[0]["teams"].items():
            if team == team3:
                team3Station = Station(station)
        if not team3Station:
            return {}

        team1Results = match1[0]["results"][team1Station.value]
        team2Results = match2[0]["results"][team2Station.value]
        team3Results = match3[0]["results"][team3Station.value]

        autoFuelTotal = (
            team1Results[-1]["autoFuelTotal"]
            + team2Results[-1]["autoFuelTotal"]
            + team3Results[-1]["autoFuelTotal"]
        )
        autoFuelTotalMissed = (
            team1Results[-1]["autoFuelTotalMissed"]
            + team2Results[-1]["autoFuelTotalMissed"]
            + team3Results[-1]["autoFuelTotalMissed"]
        )

        transitionFuelTotal = (
            team1Results[-1]["transitionFuelTotal"]
            + team2Results[-1]["transitionFuelTotal"]
            + team3Results[-1]["transitionFuelTotal"]
        )
        transitionFuelTotalMissed = (
            team1Results[-1]["transitionFuelTotalMissed"]
            + team2Results[-1]["transitionFuelTotalMissed"]
            + team3Results[-1]["transitionFuelTotalMissed"]
        )

        firstActiveShiftFuelTotal = (
            team1Results[-1]["firstActiveShiftFuelTotal"]
            + team2Results[-1]["firstActiveShiftFuelTotal"]
            + team3Results[-1]["firstActiveShiftFuelTotal"]
        )
        firstActiveShiftFuelTotalMissed = (
            team1Results[-1]["firstActiveShiftFuelTotalMissed"]
            + team2Results[-1]["firstActiveShiftFuelTotalMissed"]
            + team3Results[-1]["firstActiveShiftFuelTotalMissed"]
        )

        secondActiveShiftFuelTotal = (
            team1Results[-1]["secondActiveShiftFuelTotal"]
            + team2Results[-1]["secondActiveShiftFuelTotal"]
            + team3Results[-1]["secondActiveShiftFuelTotal"]
        )
        secondActiveShiftFuelTotalMissed = (
            team1Results[-1]["secondActiveShiftFuelTotalMissed"]
            + team2Results[-1]["secondActiveShiftFuelTotalMissed"]
            + team3Results[-1]["secondActiveShiftFuelTotalMissed"]
        )

        endgameFuelTotal = (
            team1Results[-1]["endgameFuelTotal"]
            + team2Results[-1]["endgameFuelTotal"]
            + team3Results[-1]["endgameFuelTotal"]
        )
        endgameFuelTotalMissed = (
            team1Results[-1]["endgameFuelTotalMissed"]
            + team2Results[-1]["endgameFuelTotalMissed"]
            + team3Results[-1]["endgameFuelTotalMissed"]
        )

        endgameClimbs = [
            EndPositionRebuilt(team1Results[-1]["endClimb"]),
            EndPositionRebuilt(team2Results[-1]["endClimb"]),
            EndPositionRebuilt(team3Results[-1]["endClimb"]),
        ]

        autoClimbs = [
            team1Results[-1]["autoClimbSuccess"],
            team2Results[-1]["autoClimbSuccess"],
            team3Results[-1]["autoClimbSuccess"],
        ]

        minorFouls = (
            team1Results[-1]["minorFouls"]
            + team2Results[-1]["minorFouls"]
            + team3Results[-1]["minorFouls"]
        )
        majorFouls = (
            team1Results[-1]["majorFouls"]
            + team2Results[-1]["majorFouls"]
            + team3Results[-1]["majorFouls"]
        )

        totalFuel = (
            autoFuelTotal
            + transitionFuelTotal
            + firstActiveShiftFuelTotal
            + secondActiveShiftFuelTotal
            + endgameFuelTotal
        )

        score = self.calculateScore(
            totalFuel, False, EndPositionRebuilt.NONE, minorFouls, majorFouls
        )

        for climb in autoClimbs:
            score += 15 if climb else 0

        for climb in endgameClimbs:
            score += (
                30
                if (climb == EndPositionRebuilt.L3)
                else (
                    20
                    if (climb == EndPositionRebuilt.L2)
                    else 10 if (climb == EndPositionRebuilt.L1) else 0
                )
            )

        if jsonSerializable:
            for i in range(len(endgameClimbs)):
                endgameClimbs[i] = endgameClimbs[i].value  # type: ignore

        return {
            "autoFuelTotal": autoFuelTotal,
            "autoFuelTotalMissed": autoFuelTotalMissed,
            "transitionFuelTotal": transitionFuelTotal,
            "transitionFuelTotalMissed": transitionFuelTotalMissed,
            "firstActiveShiftFuelTotal": firstActiveShiftFuelTotal,
            "firstActiveShiftFuelTotalMissed": firstActiveShiftFuelTotalMissed,
            "secondActiveShiftFuelTotal": secondActiveShiftFuelTotal,
            "secondActiveShiftFuelTotalMissed": secondActiveShiftFuelTotalMissed,
            "endgameFuelTotal": endgameFuelTotal,
            "endgameFuelTotalMissed": endgameFuelTotalMissed,
            "endgameClimbs": endgameClimbs,
            "autoClimbs": autoClimbs,
            "minorFouls": minorFouls,
            "majorFouls": majorFouls,
            "totalFuel": totalFuel,
            "score": score,
        }
