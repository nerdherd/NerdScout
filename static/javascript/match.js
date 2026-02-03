// var red_table = document.querySelector(".red-table");
// var blue_table = document.querySelector(".blue-table");

// for (var i=1;i<4;i++){
//     // red
//     // create_dropdown(red_table.querySelector(".team-"+i));
    
//     // blue
//     // create_dropdown(blue_table.querySelector(".team-"+i));
// }

// function create_dropdown(element){
//     const results_div = element.querySelector(".results-div");
//     if (results_div){
//         if (results_div.querySelectorAll(".match-data").length > 1){
//             const dropdown_button = document.createElement("div");
//             dropdown_button.id = "dropdown-"+Math.random();
//             const display_button = document.createElement("button");
//             display_button.innerText = "Viewing revision";
//             display_button.classList.add("dropdown-button");
//             display_button.onclick = () => expand_dropdown(dropdown_button.id);
//             dropdown_button.appendChild(display_button);

//             const content_div = document.createElement("div");
//             content_div.classList.add("dropdown-content-div")

//             let revision = 0;
//             for (const element of results_div.querySelectorAll(".match-data")){
//                 revision++;
//                 let new_option = document.createElement("a");
//                 new_option.href = "javascript:void(null);";
//                 new_option.dataset.revision = revision
//                 new_option.innerText = "Revision "+new_option.dataset.revision;
//                 new_option.classList.add("dropdown-element");
//                 new_option.onclick = () => set_visible(results_div,new_option.dataset.revision);
//                 content_div.appendChild(new_option);
//             }

//             dropdown_button.appendChild(content_div);

//             results_div.insertBefore(dropdown_button, results_div.firstChild);

//             display_button.innerText+=" "+revision;

//             set_visible(results_div,revision);
//         }
//     }
// }

// function expand_dropdown(id){
//     const dropdown = document.getElementById(id);

//     // for (const element of dropdown.querySelectorAll(".dropdown-content-div a")){
//     //     element.classList.toggle("show");
//     // }
//     dropdown.querySelector(".dropdown-content-div").classList.toggle("show");
// }

function get_results_div(color,index){
    return document.querySelector("."+color+"-table .team-"+index+" .results-div");
}

function set_visible(results_div,revision_id){
    for (const result of results_div.querySelectorAll(".match-data")){
        result.classList.add("hidden");
    }

    var revision = document.getElementById(revision_id).value;

    results_div.querySelector(".revision-"+revision).classList.remove("hidden");
}

// window.onclick = function(event) {
//     if (!event.target.matches('.dropdown-button')) {
//         for (const element of document.querySelectorAll(".dropdown-content-div")){
//             element.classList.remove("show");
//         }
//     }
// } 

var count = 0;
var shown = "";
function set_team(team){
    if (team != "" && shown != team){
        var show_team = "team-"+team;
        for (const team of document.querySelectorAll(".team")){
            team.classList.add("hide");
            if (team.classList.contains(show_team)){
                team.classList.remove("hide");
            }
        }
        shown = team;
        document.getElementById("score-breakdown").classList.add("hide");
    } else {
        for (const team of document.querySelectorAll(".team")){
            team.classList.add("hide"); 
        }
        document.getElementById("score-breakdown").classList.remove("hide");
        shown = "";
    }

    count++;
    if (count===2){
        document.getElementById("remove").remove();
    }
}

set_team('');


const shiftParent = document.getElementById("shiftParent");
const shifts = new Array("firstShift", "secondShift", "thirdShift", "fourthShift");
const shiftsParents = new Array("shiftOne", "shiftTwo", "shiftThree", "shiftFour");

function switchShift(shift){    
    for(let i=0; i<4; i++){
        shiftParent.classList.remove(shiftsParents.at(i));
    }
    shiftParent.classList.remove
    shiftParent.classList.add(`${shiftsParents.at(shift)}`);
}