const autoTab = document.getElementById("auto")
const teleopTab = document.getElementById("teleop")


const startPos1 = document.getElementById("SP-1")
const startPos2 = document.getElementById("SP-2")
const startPos3 = document.getElementById("SP-3")
const startPosSlider = document.getElementById("startPosSlider")
startPosSlider.value=2;

const leaveCheck = document.getElementById("leave")

const autoLevels = [
    document.getElementById("aCL1"),
    document.getElementById("aCL2"),
    document.getElementById("aCL3"),
    document.getElementById("aCL4")
]

const teleLevels = [
    document.getElementById("tCL1"),
    document.getElementById("tCL2"),
    document.getElementById("tCL3"),
    document.getElementById("tCL4")
]

//autoProcessor teleProcessor autoNet teleNet
const procNetLabels = [
    document.getElementById("aPr"),
    document.getElementById("tPr"),
    document.getElementById("aNe"),
    document.getElementById("tNe")
]


const missLabels = [
    document.getElementById("aRM"),
    document.getElementById("aPM"),
    document.getElementById("aNM"),
    document.getElementById("tRM"),
    document.getElementById("tPM"),
    document.getElementById("tNM"),
]

const missVals = [0,0,0,0,0,0]

const endPosDDown = document.getElementById("endPos")
endPosDDown.value = 1;

// let matchNum = 0
// let compLevel = 0
// let setNum = 0
// let robot = 0

let startpos = 1

let autoLeave = false

let autoReef = [0,0,0,0]
let autoReefMiss = 0
let teleReef = [0,0,0,0]
let teleReefMiss = 0

let autoProcessor = 0
let autoProcessorMiss = 0
let teleProcessor = 0
let teleProcessorMiss = 0

let autoNet = 0
let autoNetMiss = 0
let teleNet = 0
let teleNetMiss = 0

let endPos = 0
let attemptedEndPos = 0

let minorFouls = 0 
let majorFouls = 0
let comment = ""
let scout = ""


function showMatch() {
    autoTab.style.display = 'none';
    teleopTab.style.display = 'none';
}

function showAuto() {
    autoTab.style.display = 'inline';
    teleopTab.style.display = 'none';
}

function showTeleop() {
    autoTab.style.display = 'none';
    teleopTab.style.display = 'inline';
}



//autoProcessor teleProcessor autoNet teleNet
let procNetVars = [0,0,0,0]

function autoReefAdd(level){
    autoReef[level] += 1
    autoLevels[level].innerHTML = autoReef[level]
}

function teleReefAdd(level){
    teleReef[level] += 1
    teleLevels[level].innerHTML = teleReef[level]
}

function procNetAdd(level){
    procNetVars[level] += 1
    procNetLabels[level].innerHTML = procNetVars[level]
}

function autoReefSub(level){
    if(autoReef[level] != 0){
        autoReef[level] -= 1
        autoLevels[level].innerHTML = autoReef[level]
    }
}

function teleReefSub(level){
    if(teleReef[level] != 0){
        teleReef[level] -= 1
        teleLevels[level].innerHTML = teleReef[level]
    }
}

function procNetSub(level){
    if(procNetVars[level] != 0){
        procNetVars[level] -= 1
        procNetLabels[level].innerHTML = procNetVars[level]
    }
}

function missAdd(level){
    missVals[level] += 1
    missLabels[level].innerHTML = missVals[level] 
}

function missSub(level){
    if(missVals[level] != 0){
        missVals[level] -= 1
        missLabels[level].innerHTML = missVals[level] 
    }
}


//-Minor +Minor -Major +Major
function fouling(level){
    switch(level){
        case 0:
            if(minorFouls!=0){minorFouls -= 1}; break
        case 1:
            minorFouls += 1; break
        case 2:
            if(majorFouls!=0){majorFouls -= 1}; break
        case 3:
            majorFouls += 1; break
        default:
            throw(400)
    }
    document.getElementById("minF").innerHTML = minorFouls
    document.getElementById("majF").innerHTML = majorFouls
}

const positionSliderLabel = document.getElementById("positionSliderLabel");
startPosSlider.addEventListener("change",()=>{
    positionSliderLabel.innerText="Starting position: "+(["Red","Middle","Blue"])[startPosSlider.value-1];
    startpos = startPosSlider.value;
});

const endposlabel = document.getElementById("endposlabel");
endPosDDown.addEventListener("change",()=>{
    endposlabel.innerText = (["None","Park","Shallow Cage","Deep Cage"])[endPosDDown.value-1];
});

function submitData(){

    // matchNum = tMatchNum
    // compLevel = tCompLevel
    // setNum = tSetNum
    // robot = tRobot

    let section = document.getElementById("sectionInput").value;
    let matchNum = parseInt(document.getElementById("matchNumInput").value);
    let compLevel = document.getElementById("compLevelInput").value;
    let setNum = parseInt(document.getElementById("setNumInput").value);


    let startPos = 4-startPosSlider.value;
    autoLeave = (leaveCheck.value == "on")

    autoProcessor = procNetVars[0] 
    teleProcessor = procNetVars[1]
    autoNet = procNetVars[2] 
    teleNet = procNetVars[3]

    const endPosWin = !(document.getElementById("attemptEP").checked);

    attemptedEndPos = endPosDDown.value-1

    if(endPosWin){
        endPos = endPosDDown.value-1
    } else {
        endPos = 1; // assume they parked
    }

    comment = document.getElementById("comments").value

    autoReefMiss = missVals[0];
    autoProcessorMiss = missVals[1];
    autoNetMiss = missVals[2];

    teleReefMiss = missVals[3];
    teleProcessorMiss = missVals[4];
    teleNetMiss = missVals[5];


    rawData = {
        "matchNum": matchNum,
        "compLevel": compLevel,
        "setNum": setNum, 
        "robot": section,
        "startPos": startPos,
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

    downloadScore(section,matchNum,compLevel,setNum,rawData);
}