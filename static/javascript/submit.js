function toggleActive(id){
    document.getElementById(id).classList.toggle("active");
}

function updateShift(){
    // const firstShift = document.getElementById("firstShift").checked;
    // if (firstShift){
    //     document.getElementById("shift1").classList.add("active");
    //     document.getElementById("shift3").classList.add("active");
    //     document.getElementById("shift2").classList.remove("active");
    //     document.getElementById("shift4").classList.remove("active");
    // } else {
    //     document.getElementById("shift2").classList.add("active");
    //     document.getElementById("shift4").classList.add("active");
    //     document.getElementById("shift1").classList.remove("active");
    //     document.getElementById("shift3").classList.remove("active");
    // }
    setScoringPeriod(curSelected);
}

function getById(id){return document.getElementById(id);}
function getId(id,isInt=true){
    let val = getById(id).value;
    return isInt?parseInt(val):val;
}

var curScoringPeriod = 0;

function switchScoringPeriod(newPeriod){
    // curScoringPeriod=newPeriod;
    mainInputDiv.classList.add(`shift-${newPeriod}`);
    // reloadScoringTable();
}

function changeRank(tag){
    getById(`${tag}Label`).textContent = `${getId(`${tag}Rank`)}/10`
}

var revealedRanks = {
    "fed": false,
    "defending": false,
    "stole": false
}
function revealRanks(tag){
    show = false;
    for (const name of ["transition","firstActiveShift","secondActiveShift","firstInactiveShift","secondInactiveShift","endgame"]){
        show = gc(`${name}${tag}`) || show;
    }
    revealedRanks[tag] = show;
    getById(`${tag}Feedback`).style.display = show ? "flex" : "none";
}

var weWon = false;
var wonTouched = false;

var curSelected=-1;
const firstShiftCheckbox = getById("firstShift");
const mainInputDiv = getById("main-input");
//Auto Trans S1 S2 S3 S4 End
let scores = [0,0,0,0,0,0,0,0];
function setScoringPeriod(newPeriod){
    const scoreElem = document.getElementById("scored");
    scoreElem.value = scores[curSelected];
    if(newPeriod >= 1 && !wonTouched){
        alert("PLEASE PICK A SHIFT WINNER");
        return;
    }
    for (let n=0;n<7;n++) {mainInputDiv.classList.remove(`shift-${n}`);mainInputDiv.classList.remove(`shift-i${n}`);}
    mainInputDiv.classList.remove(`shift-pregame`);
    mainInputDiv.classList.remove(`shift-postgame`);
    curSelected=newPeriod;
    for (const button of document.getElementById("shift-select2").querySelectorAll("button")){
        button.classList.remove("selected");
        if (button.dataset.index==newPeriod){
            button.classList.add("selected");
            button.scrollIntoView({
                behavior:'smooth', 
                inline:'center'});
        } 
    }
    for (const button of document.getElementById("shift-select").querySelectorAll("button")){
        button.classList.remove("selected");
        if (button.dataset.index==newPeriod){
            button.classList.add("selected");
            button.scrollIntoView({
                behavior:'smooth', 
                inline:'center',
                block:'end'});
        } 
    }
    curScoringPeriod=newPeriod;
    document.getElementById("scored").value = scores[curScoringPeriod];

    if (newPeriod==-1){
        mainInputDiv.classList.add(`shift-pregame`);
        mainInputDiv.classList.add("inactive");
        return;
    }
    if (newPeriod==7){
        mainInputDiv.classList.add(`shift-postgame`);
        mainInputDiv.classList.add("inactive");
        return;
    }

    if (newPeriod==0||newPeriod==1||newPeriod==6){
        mainInputDiv.classList.remove("inactive");
        mainInputDiv.classList.add(`shift-${newPeriod}`);
        // if (newPeriod==6) switchScoringPeriod(4);
        // else switchScoringPeriod(newPeriod);
        return;
    }
    if (!weWon){
        if (newPeriod==2||newPeriod==4){
            mainInputDiv.classList.remove("inactive");
            // if (newPeriod==2) switchScoringPeriod(2);
            // if (newPeriod==4) switchScoringPeriod(3);
            if (newPeriod==2) mainInputDiv.classList.add("shift-2");
            else mainInputDiv.classList.add("shift-3")
            return
        }
        mainInputDiv.classList.add("inactive");
        if (newPeriod==3) mainInputDiv.classList.add(`shift-i1`);
        if (newPeriod==5) mainInputDiv.classList.add(`shift-i2`);
        return;
    }
    if (newPeriod==3||newPeriod==5){
        mainInputDiv.classList.remove("inactive");
        // if (newPeriod==3) switchScoringPeriod(2);
        // if (newPeriod==5) switchScoringPeriod(3);
        if (newPeriod==3) mainInputDiv.classList.add("shift-2");
        else mainInputDiv.classList.add("shift-3")
        return
    }
    if (newPeriod==2) mainInputDiv.classList.add(`shift-i1`);
    if (newPeriod==4) mainInputDiv.classList.add(`shift-i2`);
    mainInputDiv.classList.add("inactive");
}

function incrementCounter(id,isPositive,amount=1){
    const curElement = document.getElementById(id);
    for (let i=0;i<amount;i++){
        if (isPositive){
            curElement.value++;
            // scores[curElement] = curElement.value;
        } 
        else if (curElement.value > 0){
            curElement.value--;
            // scores[curElement] = curElement.value;
        } 
    }
}

function incrementFuelCounter(id,isPositive,amount=1){
    incrementCounter(id,isPositive,amount);
    scores[curScoringPeriod] = parseInt(document.getElementById(id).value);
}

setScoringPeriod(-1)

const redWinCheck = getById("redFirstShift")
const blueWinCheck = getById("blueFirstShift")
const errorMsg = getById("winnerNotPicked")

const attemptSlider = getById("attemptEndDiv")
const climbFailCheck = getById("climbFail")

var endFail = false;

function attemptEnd(){
    endFail = climbFailCheck.checked;
    if(endFail){
        attemptSlider.style.display = "flex";
    }else{
        attemptSlider.style.display = "none";
        const val = getId('attemptedEndClimb');
        document.getElementById('endClimb').value = val;
        endGameText.textContent = "Actual End Position: ".concat(climbPos[val]);
    }
}

function redTeamWon(color){
    if(color=="Red"){
        weWon = true;
    } else {
        weWon = false;
    }
    wonTouched = true;
    errorMsg.style.display = "none";
    redWinCheck.disabled = true;
    blueWinCheck.disabled = false;
    blueWinCheck.checked = false;
}

function blueTeamWon(color){
    if(color=="Blue"){
        weWon = true;
    } else {
        weWon = false;
    }
    wonTouched = true;
    errorMsg.style.display = "none";
    blueWinCheck.disabled = true;
    redWinCheck.disabled = false;
    redWinCheck.checked = false;
}



// get checked
function gc(id){ return getById(id).checked; }

function submitData(matchNum, compLevel, setNum, robot){

    // matchNum = tMatchNum
    // compLevel = tCompLevel
    // setNum = tSetNum
    // robot = tRobot

    cannedComments = []

    for (const button of document.querySelectorAll(".canned-button.active")){
        cannedComments.push(button.dataset.text);
    }

    // comment = document.getElementById("comments").value


    rawData = {
        "matchNum": matchNum,
        "compLevel": compLevel,
        "setNum": setNum, 
        "robot": robot,
        "startPos": getId("startposinput"),
        "preloadFuel": getId("preloadFuel"),
        "autoFuelTotal": scores[0],
        "autoDepot": gc("autoDepot"),
        "autoBump": gc("autoBump"),
        "autoTrench": gc("autoTrench"),
        "autoNeutralIntake": gc("autoNeutralIntake"),
        "autoAttemptedSecondScore": gc("autoAttemptedSecondScore"),
        "autoSucceededSecondScore": gc("autoSucceededSecondScore"),
        "autoClimbAttempted": gc("autoClimbAttempted"),
        "autoClimbSuccess": gc("autoClimbSuccess"),
        "autoOutpostFeed": gc("autoOutpostFeed"),
        "autoFedToOutpost": gc("autoFedToOutpost"),
        "firstShift": !weWon,
        "transitionFuelTotal": scores[1],
        "transitionFed": gc("transitionfed"),
        "transitionDefense": gc("transitiondefending"),
        "transitionStole": gc("transitionstole"),
        "firstActiveShiftFuelTotal": scores[(weWon)?3:2],
        "firstActiveShiftFed": gc("firstActiveShiftfed"),
        "firstActiveShiftDefense": gc("firstActiveShiftdefending"),
        "firstActiveShiftStole": gc("firstActiveShiftstole"),
        "secondActiveShiftFuelTotal": scores[(weWon)?5:4],
        "secondActiveShiftFed": gc("secondActiveShiftfed"),
        "secondActiveShiftDefense": gc("secondActiveShiftdefending"),
        "secondActiveShiftStole": gc("secondActiveShiftstole"),
        "firstInactiveShiftScored": gc("firstInactiveShiftScored"),
        "firstInactiveShiftFed": gc("firstInactiveShiftfed"),
        "firstInactiveShiftDefense": gc("firstInactiveShiftdefending"),
        "firstInactiveShiftStole": gc("firstInactiveShiftstole"),
        "firstInactiveShiftIntaked": gc("firstInactiveShiftIntaked"),
        "secondInactiveShiftScored": gc("secondInactiveShiftScored"),
        "secondInactiveShiftFed": gc("secondInactiveShiftfed"),
        "secondInactiveShiftDefense": gc("secondInactiveShiftdefending"),
        "secondInactiveShiftStole": gc("secondInactiveShiftstole"),
        "secondInactiveShiftIntaked": gc("secondInactiveShiftIntaked"),
        "endgameFuelTotal": scores[6],
        "endgameFed": gc("endgamefed"),
        "endgameDefense": gc("endgamedefending"),
        "endgameStole": gc("endgamestole"),
        "endClimb": getId("endClimb"),
        "endClimbAttempted": getId("attemptedEndClimb"),
        "outpostIntake": gc("outpostIntake"),
        "groundIntake": gc("groundIntake"),
        "fedToOutpost": gc("fedToOutpost"),
        "feedingRank": revealedRanks["fed"] ? getId("feedingRank") : null,
        "feedingComment": getId("feedingComment", false),
        "defenseRank": revealedRanks["defending"] ? getId("defendingRank") : null,
        "defenseComment": getId("defendingComment", false),
        "driverRank":getId("driverRank"),
        "vibeCheck":getId("vibeRank"),
        "stealRank": revealedRanks["stole"] ? getId("stoleRank") : null,
        "minorFouls": getId("minorFouls"),
        "majorFouls": getId("majorFouls"),  
        "comment": getId("comments",false),  
        "cannedComments": cannedComments,  
    };
    data = JSON.stringify(rawData);
    console.log(rawData);
    console.log(data);
    fetch(window.location.href, {
        method: "POST",
        body: data, 
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(response =>{
        if (response.ok){
            alert("Succesfully submitted")
            redirect_to_match()
        } else{
            alert("There was an error submitting.");
        }
    });
}

// const preGame = getById("preGame");
// const game = getById("game");
// const postGame = getById("postGame");

// function showPreGame(){
//     preGame.style.display = 'flex';
//     game.style.display = 'none';
//     postGame.style.display = 'none';
// }

// function showGame(){
//     preGame.style.display = 'none';
//     game.style.display = 'flex';
//     postGame.style.display = 'none';
// }

// function showPostGame(){
//     preGame.style.display = 'none';
//     game.style.display = 'none';
//     postGame.style.display = 'flex';
// }

const endGameText = getById('EndPosText');
const attemptEndGameText = getById('AttemptEndPosText');
const climbPos = ["Ground", "Level 1", "Level 2", "Level 3"]

function accChangeText(){
    const val = getId('endClimb');
    let template = "Actual End position: ";
    endGameText.textContent = template.concat(climbPos[val]);
}
function endChangeText(){
    const val = getId('attemptedEndClimb');
    let template = "Attempted End position: ";
    attemptEndGameText.textContent = template.concat(climbPos[val]);
    if (!endFail){
        document.getElementById('endClimb').value = val;
        endGameText.textContent = "Actual End Position: ".concat(climbPos[val]);
    }
}