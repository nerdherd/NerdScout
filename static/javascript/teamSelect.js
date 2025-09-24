const teamNameInput = document.getElementById("teamNameInput");
const teamNumInput = document.getElementById("teamNumInput");

const teamNameExact = document.getElementById("teamNameExact");
const teamNumExact = document.getElementById("teamNumExact");

function updateSearch(){
    let nameInput = teamNameInput.value.toLowerCase();
    let nameEmpty = (nameInput === "");
    let nameExact = teamNameExact.checked;

    let numInput = teamNumInput.value;
    let numEmpty = (numInput === "");
    let numExact = teamNumExact.checked;

    let noneFound = true;
    for (const teamDiv of document.querySelectorAll(".team-div")){
        teamDiv.classList.add("hide");

        let teamName = teamDiv.dataset.name.toLowerCase();
        let nameValid = nameExact ? (teamName === nameInput):teamName.includes(nameInput);

        let teamNum = teamDiv.dataset.num;
        let numValid = numExact ? (teamNum === numInput) : teamNum.includes(numInput)

        if ((nameEmpty || nameValid) && (numEmpty || numValid)){
            teamDiv.classList.remove("hide");
            noneFound = false;
        }
    }
}