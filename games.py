
from constants import *
from pymongo.collection import Collection

class Game:
    """
    Game Superclass

    This shouldn't be used; all functions should be replaced.
    """
    def __init__(self, matches:Collection, teams:Collection):
        self.keyDisplayNames = {}
        self.matches = matches
        self.teams = teams
    def calculateScore(self) -> int:
        """
        Calculate the total score from scouted values.

        This shouldn't be used; replace this with a game specific function.
        
        Inputs:
        - Depends
        
        Outputs:
        - int: total score, minus points from fouls
        
        """
        return 0
    def scoreRobotInMatch(self) -> bool:
        """
        Scores one robot in a match.

        This shouldn't be used; replace this with a game specific function.

        Inputs:
        - self explanitory
        
        Returns:
        - Boolean: if the robot was successfully scored
        """
        return False
    def calculateScoreFromData(self, matchData: dict, team: Station, edit: int = -1) -> int:
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
        return 0
    
class Reefscape(Game):
    def __init__(self, matches:Collection, teams:Collection):
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
                                self,
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
        def calculateScoreFromData(matchData: dict, team: Station, edit: int = -1) -> int:
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
            score = calculateScore(
                self,
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