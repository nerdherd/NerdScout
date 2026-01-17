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

function incrementCounter(id,isPositive){
    const curElement = document.getElementById(id);
    if (isPositive) curElement.value++;
    else if (curElement.value > 0) curElement.value--;
}

function getId(id){return document.getElementById(id).value;}

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
        "autoFuel": getId("autoFuel"),
        "autoFuelMiss": getId("autoFuelMiss"),
        "autoClimb": document.getElementById("autoClimb").checked,
        "firstShift": document.getElementById("firstShift").checked,
        "transitionFuel": getId("transitionFuel"),
        "transitionFuelMiss": getId("transitionFuelMiss"),
        "shift1Fuel": getId("shift1Fuel"),
        "shift1FuelMiss": getId("shift1FuelMiss"),
        "shift2Fuel": getId("shift2Fuel"),
        "shift2FuelMiss": getId("shift2FuelMiss"),
        "shift3Fuel": getId("shift3Fuel"),
        "shift3FuelMiss": getId("shift3FuelMiss"),
        "shift4Fuel": getId("shift4Fuel"),
        "shift4FuelMiss": getId("shift4FuelMiss"),
        "endgameFuel": getId("endgameFuel"),
        "endgameFuelMiss": getId("endgameFuelMiss"),
        "attemptedEndPos": getId("attemptedEndPos"),
        "minorFouls": getId("minorFouls"),
        "majorFouls": getId("majorFouls"),  
        "comment": getId("comments"),  
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