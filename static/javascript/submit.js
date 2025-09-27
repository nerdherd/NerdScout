const autoTab = document.getElementById("auto")
const teleopTab = document.getElementById("teleop")
const matchNumInp = document.getElementById("matchNumberInput")
const teamNumInp = document.getElementById("teamNumberInput")
const compDropdown = document.getElementById("compLevel")

let matchNum = 0
let compLevel = 0
let setNum = 0
let robot = 0
let startpos = 0
let autoLeave = 0
let autoReef = 0 
let teleReef = 0
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

function submitData(tMatchNum, tCompLevel, tSetNum, tRobot){

    matchNum = tMatchNum
    compLevel = tCompLevel
    setNum = tSetNum
    robot = tRobot







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
        "scout": scout
    };
    alert(JSON.stringify(rawData))



    // data = JSON.stringify(rawData)
    // fetch(window.location.href, {
    // method: "POST",
    // body: data, 
    // headers: {
    //     "Content-type": "application/json; charset=UTF-8"
    // }
    // }    );
}

