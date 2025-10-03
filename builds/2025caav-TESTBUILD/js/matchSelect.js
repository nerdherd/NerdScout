const fileInput = document.getElementById("scheduleInput");

function addFiles(){
    var file = fileInput.files[0];
    var rawData;
    if (file) {
        var reader = new FileReader();
        reader.readAsText(file, "UTF-8");
        reader.onload = function (evt) {
            handleJson(evt.target.result);
        }
        reader.onerror = function (evt) {
            console.log("error reading file");
            return;
        }
    }
}

var data;
function handleJson(rawData){
    data = JSON.parse(rawData);
    // console.log(data);
    addMatches();
}

function addMatches(){
    let matchesDiv = document.getElementById("matches");
    let scoutUrl = "./scout.html";
    for (const match of data){
        var curDiv = document.createElement("div");
        curDiv.classList.add("match-div");

        curDiv.dataset.complevel = match.compLevel;
        curDiv.dataset.matchnumber = match.matchNumber;
        curDiv.dataset.setnumber = match.setNumber;

        curDiv.dataset.teams = Object.values(match.teams).join(",");
        
        let matchLink = `${scoutUrl}?matchNum=${match.matchNumber}&setNum=${match.setNumber}&compLevel=${match.compLevel}`;

        curDiv.innerHTML = `<h2>${match.displayName}</h2>
    <p>Red teams: 
        <a href="${matchLink}&station=red1">${match.teams.red1}</a>, 
        <a href="${matchLink}&station=red2">${match.teams.red2}</a>,
        <a href="${matchLink}&station=red3">${match.teams.red3}</a>
    </p>
    <p>Blue teams: 
        <a href="${matchLink}&station=blue1">${match.teams.blue1}</a>, 
        <a href="${matchLink}&station=blue2">${match.teams.blue2}</a>,
        <a href="${matchLink}&station=blue3">${match.teams.blue3}</a>
    </p>`
        matchesDiv.insertBefore(curDiv,matchesDiv.lastElementChild);
    }
}

const noneDiv = document.getElementById("none-div");

const matchNumberInput = document.getElementById("matchNumberInput");
const teamNumberInput = document.getElementById("teamNumberInput");

const qmSelect = document.getElementById("qm-select");
const efSelect = document.getElementById("ef-select");
const qfSelect = document.getElementById("qf-select");
const sfSelect = document.getElementById("sf-select");
const  fSelect = document.getElementById("f-select");

function updateSearch(){
    let matchInput = matchNumberInput.value;
    let matchEmpty = (matchInput === "");

    let teamInput = teamNumberInput.value;
    let teamEmpty = (teamInput === "");

    let compLevels = [];
    if (qmSelect.checked){compLevels.push("qm");}
    if (efSelect.checked){compLevels.push("ef");}
    if (qfSelect.checked){compLevels.push("qf");}
    if (sfSelect.checked){compLevels.push("sf");}
    if (fSelect.checked){compLevels.push("f");}

    let noneFound = true;

    for (const matchDiv of document.querySelectorAll(".match-div")){
        console.log(matchDiv);
        matchDiv.classList.add("hide");

        let compLevel = matchDiv.dataset.complevel;

        let teams = (matchDiv.dataset.teams).split(",");

        let matchNum = (compLevel==="sf")?matchDiv.dataset.setnumber:matchDiv.dataset.matchnumber;

        if ((matchEmpty || matchNum.includes(matchInput)) && compLevels.includes(compLevel) && (teamEmpty || teams.includes(teamInput))){
            matchDiv.classList.remove("hide");
            noneFound = false;
        }
    }

    noneDiv.classList.add("hide");
    if (noneFound){
        noneDiv.classList.remove("hide");
    }
}

updateSearch();