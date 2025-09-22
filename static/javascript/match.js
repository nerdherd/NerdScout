var red_table = document.querySelector(".red-table");
var blue_table = document.querySelector(".blue-table");

for (var i=1;i<4;i++){
    // red
    create_dropdown(red_table.querySelector(".team-"+i));
}

function create_dropdown(element){
    const results_div = element.querySelector(".results-div");
    if (results_div){
        console.log(results_div.children);
    }
}