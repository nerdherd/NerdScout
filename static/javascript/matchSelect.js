const matchNumberInput = document.getElementById("matchNumberInput");

const qmSelect = document.getElementById("qm-select");
const efSelect = document.getElementById("ef-select");
const qfSelect = document.getElementById("qf-select");
const sfSelect = document.getElementById("sf-select");
const  fSelect = document.getElementById("f-select");

function updateSearch(){
    let matchInput = matchNumberInput.value;
    console.log(matchInput);
    let matchEmpty = (matchInput === "");
    let compLevels = [];
    if (qmSelect.checked){compLevels.push("qm");}
    if (efSelect.checked){compLevels.push("ef");}
    if (qfSelect.checked){compLevels.push("qf");}
    if (sfSelect.checked){compLevels.push("sf");}
    if (fSelect.checked){compLevels.push("f");}

    for (const matchDiv of document.querySelectorAll(".match-div")){
        matchDiv.classList.add("hide");

        let compLevel = matchDiv.dataset.complevel;



        if ((matchEmpty || matchDiv.dataset.matchnumber.includes(matchInput)) && compLevels.includes(compLevel)){
            matchDiv.classList.remove("hide");
        }
    }
}

updateSearch();