function submitData(){
    rawData = {
        "matchNum": matchNum,
        "compLevel": compLevel,
        "setNum": setNum, 
        "robot": robot,
        "startPos": startpos,
        "autoLeave": autoLeave,
        "autoReef": autoReef,
        "autoReefMiss": autoReefMiss,
        "teleReef": teleReef,
        "teleReefMiss": teleReefMiss,
        "autoProcessor": autoProcessor,
        "autoProcessorMiss": autoProcessorMiss,
        "teleProcessor": teleProcessor,
        "teleProcessorMiss": teleProcessorMiss,
        "autoNet": autoNet,
        "autoNetMiss": autoNetMiss,
        "teleNet": teleNet,
        "teleNetMiss": teleNetMiss,
        "endPos": endPos,
        "attemptedEndPos": attemptedEndPos,
        "minorFouls": minorFouls,
        "majorFouls": majorFouls,
        "comment": comment
    };
    data = JSON.stringify(rawData);
}