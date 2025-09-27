const autoTab = document.getElementById("auto")
const teleopTab = document.getElementById("teleop")


const startPos1 = document.getElementById("SP-1")
const startPos2 = document.getElementById("SP-2")
const startPos3 = document.getElementById("SP-3")

const leaveCheck = document.getElementById("leave")

const autoLevels = [document.getElementById("aCL1"),
    document.getElementById("aCL2"),
    document.getElementById("aCL3"),
    document.getElementById("aCL4")]

const teleLevels = [document.getElementById("tCL1"),
    document.getElementById("tCL2"),
    document.getElementById("tCL3"),
    document.getElementById("tCL4")]

//autoProcessor teleProcessor autoNet teleNet
const procNetLabels = [document.getElementById("aPr"),
    document.getElementById("tPr"),
    document.getElementById("aNe"),
    document.getElementById("tNe")]

const endPosDDown = document.getElementById("endPos")

let matchNum = 0
let compLevel = 0
let setNum = 0
let robot = 0

let startpos = 0

let autoLeave = false

let autoReef = [0,0,0,0]
let teleReef = [0,0,0,0]

let autoProcessor = 0
let teleProcessor = 0

let autoNet = 0
let teleNet = 0

let endPos = 0

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


function setStartPos(pos){
    startpos = pos
    let poss = [startPos1, startPos2, startPos3]
    for(let i=0;i<3;i++){
        poss[i].disabled = false
        if(i==pos-1){
            poss[i].disabled = true
        }
    }
    poss[pos-1].disabled = true;
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

function submitData(tMatchNum, tCompLevel, tSetNum, tRobot){

    matchNum = tMatchNum
    compLevel = tCompLevel
    setNum = tSetNum
    robot = tRobot

    autoLeave = (leaveCheck.value == "on")

    autoProcessor = procNetVars[0] 
    teleProcessor = procNetVars[1]
    autoNet = procNetVars[2] 
    teleNet = procNetVars[3]

    endPos = endPosDDown.value

    comment = document.getElementById("Comments").value




    rawData = {
        "matchNum": matchNum,
        "compLevel": compLevel,
        "setNum": setNum, 
        "robot": robot,
        "startPos": startpos,
        "autoLeave": autoLeave,
        "autoReef": autoReef,
        "teleReef": teleReef,
        "autoProcessor": autoProcessor,
        "teleProcessor": teleProcessor,
        "autoNet": autoNet,
        "teleNet": teleNet,
        "endPos": endPos,
        "minorFouls": minorFouls,
        "majorFouls": majorFouls,
        "comment": comment,
    };
    data = JSON.stringify(rawData)
    fetch(window.location.href, {
    method: "POST",
    body: data, 
    headers: {
        "Content-type": "application/json; charset=UTF-8"
    }
    });
}

