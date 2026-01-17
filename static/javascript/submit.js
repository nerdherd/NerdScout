const startPosCanvas = document.getElementById("startPosCanvas");
const startPosCtx = startPosCanvas.getContext("2d");

function updateMousePos(e) {
    let rect = startPosCanvas.getBoundingClientRect();

    startPosX = (e.clientX - rect.left) * startPosCanvas.width / rect.width;
    startPosY = (e.clientY - rect.top) * startPosCanvas.height / rect.height;
}

var mouseDown = 0;
document.body.onmousedown = function() { 
    ++mouseDown;
}
document.body.onmouseup = function() {
    --mouseDown;
}

startPosCanvas.addEventListener("mousemove", (e) => {
    if (mouseDown) {
        updateMousePos(e);
        requestAnimationFrame(drawStartPos);
    }
});

startPosCanvas.addEventListener("click", (e) => {
    updateMousePos(e);
    requestAnimationFrame(drawStartPos);
});

var startPosX = startPosCanvas.width/2;
var startPosY = startPosCanvas.height/2;
var lastX = startPosX;
var lastY = startPosY;
function drawStartPos(){
    let dx = Math.abs(startPosX-lastX), dy = Math.abs(startPosY-lastY)
    let isDifferent = (dx>1||dy>1);
    let isClose = (dx<10&&dy<10);
    if (isDifferent){
        if (isClose){
            if (startPosX>lastX) lastX++;
            else if (startPosX<lastX) lastX--;
            if (startPosY>lastY) lastY++;
            else if (startPosY<lastY) lastY--;
        } else {
            lastX = Math.round(0.2*startPosX + 0.8*lastX);
            lastY = Math.round(0.2*startPosY + 0.8*lastY);
        }
    } else {
        lastX = startPosX;
        lastY = startPosY; 
    }

    startPosCtx.clearRect(0,0,startPosCanvas.width,startPosCanvas.height);
    startPosCtx.beginPath();
    startPosCtx.rect(lastX-15,lastY-15,30,30);
    startPosCtx.fillStyle = "gray";
    startPosCtx.fill();

    if (isDifferent) requestAnimationFrame(drawStartPos);
}
requestAnimationFrame(drawStartPos);

function toggleActive(id){
    document.getElementById(id).classList.toggle("active");
}

function updateShift(){
    const firstShift = document.getElementById("firstShift").checked;
    if (firstShift){
        document.getElementById("shift1").classList.add("active");
        document.getElementById("shift3").classList.add("active");
        document.getElementById("shift2").classList.remove("active");
        document.getElementById("shift4").classList.remove("active");
    } else {
        document.getElementById("shift2").classList.add("active");
        document.getElementById("shift4").classList.add("active");
        document.getElementById("shift1").classList.remove("active");
        document.getElementById("shift3").classList.remove("active");
    }
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

var scoringPeriods = [];
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
    // let scored = parseInt(scoredElemenet.value);
    // let missed = parseInt(missedElemenet.value);
    // scoringPeriods.push({"time":elapsed,"scored":scored,"missed":missed});
    // scoredElemenet.value = 0;
    // missedElemenet.value = 0;
    timer_button.innerText = "Start Timer";
    timer_input.value = elapsed
    // addScoreToTable(elapsed,scored,missed);
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
    cur_row.appendChild(timeEl);
    cur_row.appendChild(scoredEl);
    cur_row.appendChild(missedEl);
    score_table.appendChild(cur_row)
}

function submitScoringPeriod(){
    let scored = parseInt(scoredElemenet.value);
    let missed = parseInt(missedElemenet.value);
    let time = parseFloat(timer_input.value);
    scoringPeriods.push({"time":time,"scored":scored,"missed":missed});
    scoredElemenet.value = 0;
    missedElemenet.value = 0;
    timer_input.value = 0;
    addScoreToTable(time,scored,missed);
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
        "startPosX": startPosY/startPosCanvas.height,
        "startPosY": startPosX/startPosCanvas.width,
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