var rows = Array.prototype.slice.call(document.querySelectorAll(".team-row"));
const mainTable = document.getElementById("main-table");

function updateSort(){
    sortCategory = document.getElementById("sort-category").value;

    rowNodes = document.querySelectorAll(".team-row");

    rows = Array.prototype.slice.call(rowNodes);

    for (const row of rowNodes){
        row.remove();
    }

    rows.sort(function(a,b){
        var aVal = a.dataset[sortCategory];
        var bVal = b.dataset[sortCategory];
        if (aVal > bVal) return 1;
        if (aVal < bVal) return -1;
        return 0;
    });
    if (document.getElementById("sort-input").value == "descending"){
        rows = rows.reverse();
    }
    
    rows.forEach(element => {
        mainTable.appendChild(element);
    });;
}