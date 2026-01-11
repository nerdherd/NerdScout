function toggleActive(id){
    document.getElementById(id).classList.toggle("active");
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
        "startPosX": 0.0,
        "startPosY": 0.0,
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
        "minorFouls": 1,
        "majorFouls": 1,  
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