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

function incrementCounter(id,isPositive,amount=1){
    const curElement = document.getElementById(id);
    for (let i=0;i<amount;i++){
        if (isPositive) curElement.value++;
        else if (curElement.value > 0) curElement.value--
    }
}

function getById(id){return document.getElementById(id);}
function getId(id,isInt=true){
    let val = getById(id).value;
    return isInt?parseInt(val):val;
}

var curScoringPeriod = 0;
var scoringPeriods = [[],[],[],[],[]]; // auto, transition, first active, second active, endgame
var timerActive = false;
var startTime;
var scoredElemenet = getById("scored"); // speleld wrong
var missedElemenet = getById("missed");
function toggleTimer(){
    if (!timerActive){
        startTime = Date.now();
        timerActive = true;
        requestAnimationFrame(drawTimer);
        timer_button.innerText = "Stop Timer";
        return;
    }
    timerActive = false;
    let elapsed = (Date.now()-startTime)/1000;
    timer_button.innerText = "Start Timer";
    timer_input.value = elapsed
}

var timer_button = getById("timer-button");
var timer_input = getById("time");
function drawTimer(){
    timer_input.value = (Date.now()-startTime)/1000;
    if (timerActive) requestAnimationFrame(drawTimer);
}

var score_table = getById("score-table");
function addScoreToTable(time,scored,missed){
    let cur_row = document.createElement("tr");
    let timeEl = document.createElement("td");
    timeEl.innerText=time;
    let scoredEl = document.createElement("td");
    scoredEl.innerText=scored;
    let missedEl = document.createElement("td");
    missedEl.innerText=missed;
    let deleteTableEl = document.createElement("td")
    let deleteButton = document.createElement("button");
    deleteButton.innerText = "X";
    let deleteIndex = scoringPeriods[curScoringPeriod].length-1;
    deleteButton.onclick = () => {removeScore(deleteIndex)};
    deleteTableEl.appendChild(deleteButton);
    cur_row.appendChild(timeEl);
    cur_row.appendChild(scoredEl);
    cur_row.appendChild(missedEl);
    cur_row.appendChild(deleteTableEl);
    score_table.appendChild(cur_row)
}

function submitScoringPeriod(){
    let scored = parseInt(scoredElemenet.value);
    let missed = parseInt(missedElemenet.value);
    let time = parseFloat(timer_input.value);
    if (time <= 0.01) {
        alert("please put more time!");
        return;
    }
    scoringPeriods[curScoringPeriod].push({"time":time,"scored":scored,"missed":missed});
    scoredElemenet.value = 0;
    missedElemenet.value = 0;
    timer_input.value = 0;
    addScoreToTable(time,scored,missed);
}

function addScoresToTable(scores){
    for (const scoringPeriod of scores){
        addScoreToTable(scoringPeriod["time"],scoringPeriod["scored"],scoringPeriod["missed"]);
    }
}

function removeScore(index){
    scoringPeriods[curScoringPeriod].splice(index,1);
    reloadScoringTable();
}

function switchScoringPeriod(newPeriod){
    curScoringPeriod=newPeriod;
    mainInputDiv.classList.add(`shift-${newPeriod}`);
    reloadScoringTable();
}

var curSelected=0;
const firstShiftCheckbox = getById("firstShift");
const mainInputDiv = getById("main-input");
function setScoringPeriod(newPeriod){
    for (let n=0;n<7;n++) {mainInputDiv.classList.remove(`shift-${n}`);mainInputDiv.classList.remove(`shift-i${n}`);}
    curSelected=newPeriod;
    for (const button of document.getElementById("shift-select").querySelectorAll("button")){
        button.classList.remove("selected");
        if (button.dataset.index==newPeriod) button.classList.add("selected");
    }
    if (newPeriod==0||newPeriod==1||newPeriod==6){
        mainInputDiv.classList.remove("inactive");
        mainInputDiv.classList.add(`shift-${newPeriod}`);
        if (newPeriod==6) switchScoringPeriod(4);
        else switchScoringPeriod(newPeriod);
        return;
    }
    if (firstShiftCheckbox.checked){
        if (newPeriod==2||newPeriod==4){
            mainInputDiv.classList.remove("inactive");
            if (newPeriod==2) switchScoringPeriod(2);
            if (newPeriod==4) switchScoringPeriod(3);
            return
        }
        mainInputDiv.classList.add("inactive");
        if (newPeriod==3) mainInputDiv.classList.add(`shift-i1`);
        if (newPeriod==5) mainInputDiv.classList.add(`shift-i2`);
        return;
    }
    if (newPeriod==3||newPeriod==5){
        mainInputDiv.classList.remove("inactive");
        if (newPeriod==3) switchScoringPeriod(2);
        if (newPeriod==5) switchScoringPeriod(3);
        return
    }
    if (newPeriod==2) mainInputDiv.classList.add(`shift-i1`);
    if (newPeriod==4) mainInputDiv.classList.add(`shift-i2`);
    mainInputDiv.classList.add("inactive");
}

function reloadScoringTable(){
    for (const row of score_table.querySelectorAll("tr:not(.headers)")){
        row.remove();
    }
    addScoresToTable(scoringPeriods[curScoringPeriod]);
}

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
        "startPosX": getId("startposinput"),
        "preloadFuel": getId("preloadFuel"),
        // TODO: add this
        "minorFouls": getId("minorFouls"),
        "majorFouls": getId("majorFouls"),  
        "comment": getId("comments",false),  
        "cannedComments": cannedComments,  
    };
    data = JSON.stringify(rawData);
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
    });;
}