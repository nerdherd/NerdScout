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
        var aVal = parseFloat(a.dataset[sortCategory]);
        var bVal = parseFloat(b.dataset[sortCategory]);
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

    for (const button of document.querySelectorAll("th button")){
        button.classList.remove("title-selected");
        if (button.classList.contains("header-button-"+sortCategory)){
            button.classList.add("title-selected");
        }
    }
}

function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseFloat(str))
}

function download_table_as_csv(isMatches=false,separator = ',') {
    var rows = document.querySelectorAll('table#main-table tr');
    var csv = [];
    for (var i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("hidden")){
            continue;
        }
        var row = [], cols = rows[i].querySelectorAll('td, th');
        for (var j = 0; j < cols.length; j++) {
            if (cols[j].classList.contains("hidden")){
                continue;
            }

            if (cols[j].nodeName==="TH" || isNaN(cols[j].innerText) || isNaN(parseFloat(cols[j].innerText))){
                // Clean innertext to remove multiple spaces and jumpline (break csv)
                var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ')
                // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
                data = data.replace(/"/g, '""');
                // Push escaped string
                row.push('"' + data + '"');
            } else {
                var data = cols[j].innerText;
                row.push(data);
            }
        }
        csv.push(row.join(separator));
    }
    var csv_string = csv.join('\n');
    // Download it
    var filename;
    if (!isMatches) {filename = 'export_teams_' + new Date().toLocaleDateString() + '.csv'}
    else {filename = 'export_matches_' + new Date().toLocaleDateString() + '.csv'};
    var link = document.createElement('a');
    link.style.display = 'none';
    link.setAttribute('target', '_blank');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function setSort(value){
    let options = document.getElementById("sort-category").querySelectorAll("option");
    for (const option of options){
        let selected = (option.value === value);
        if (option.selected&&selected){
            for (const orderoption of document.getElementById("sort-input").querySelectorAll("option")){
                orderoption.toggleAttribute("selected");
            }
        }
        option.selected = selected;
    }
    updateSort();
}

function setColumns(){
    const columnSelectDiv = document.getElementById("column-select");
    let allowedColumns = ["column-team"];
    for (const checkbox of columnSelectDiv.querySelectorAll("input")){
        if (checkbox.checked){
            allowedColumns.push("column-"+checkbox.dataset.value);
        }
    }

    console.log(allowedColumns);


    let rowNodes = mainTable.querySelectorAll("tr");
    for (const rowNode of rowNodes){
        for (const element of rowNode.children){
            element.classList.add("hidden");
            for (const curClass of element.classList){
                if (allowedColumns.includes(curClass)){
                    element.classList.remove("hidden");
                }
            }
        }
    }
}

function setRows(){
    const teamSelectDiv = document.getElementById("team-select");
    let allowedRows = ["header-row"];
    for (const checkbox of teamSelectDiv.querySelectorAll("input")){
        if (checkbox.checked){
            allowedRows.push("row-"+checkbox.dataset.team);
        }
    }
    let rowNodes = mainTable.querySelectorAll("tr");
    for (const rowNode of rowNodes){
        rowNode.classList.add("hidden");
        for (const curClass of rowNode.classList){
            if (allowedRows.includes(curClass)){
                rowNode.classList.remove("hidden");
            }
        }
    }
}