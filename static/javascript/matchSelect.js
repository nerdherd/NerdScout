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
        matchDiv.classList.add("hide");

        let compLevel = matchDiv.dataset.complevel;

        let teams = (matchDiv.dataset.redteams+","+matchDiv.dataset.blueteams).split(",");

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