const teamInputEl = document.getElementById("teamInput");
const teamExactEl = document.getElementById("teamExact");
const searchTypeEl = document.getElementById("searchType");

function updateSearch(){
    let teamInput = teamInputEl.value.toLowerCase();
    let teamEmpty = (teamInput === "");
    let teamExact = teamExactEl.checked;
    let searchType = searchTypeEl.value;

    let noneFound = true;
    for (const teamDiv of document.querySelectorAll(".team-div")){
        teamDiv.classList.add("hide");

        let teamName = teamDiv.dataset.name.toLowerCase();
        let nameValid = teamExact ? (teamName === teamInput):teamName.includes(teamInput);

        let teamNum = teamDiv.dataset.num;
        let numValid = teamExact ? (teamNum === teamInput) : teamNum.includes(teamInput);

        let valid = (teamEmpty || (searchType === "name" && nameValid) || (searchType==="number" && numValid));

        if (valid){
            teamDiv.classList.remove("hide");
            noneFound = false;
        }
    }
}