// var rows = Array.from(document.querySelectorAll(".row"));
const table = document.getElementById("table");

function updateSort(){
    let sortCategory = document.getElementById("sort-category").value;
    let descending = (document.getElementById("sort-input").value === "descending");

    let rows = Array.from(document.querySelectorAll(".row"));

    rows.sort((a,b) => {
        var aRaw = a.dataset[sortCategory];
        var bRaw = b.dataset[sortCategory];
        if (aRaw === "True" || aRaw === "False"){
            // true vs false
            if (aRaw === bRaw) return 0;
            if (aRaw === "") return descending ? -1 : 1;
            if (bRaw === "") return descending ? 1 : -1;
            if (aRaw === "True") return 1;
            if (bRaw === "True") return -1;
            return 0;
            // return -1;
        }
        var aVal = parseFloat(aRaw);
        var bVal = parseFloat(bRaw);
        if (sortCategory === "displayname"){
            // display name
            let aSplit = aRaw.split(" ");
            let bSplit = bRaw.split(" ");
            // get match number
            aVal = parseInt(aSplit[1]);
            bVal = parseInt(bSplit[1]);
            // offset different match types
            if (aSplit[0] === "Final") aVal+=20000;
            if (bSplit[0] === "Final") bVal+=20000;
            if (aSplit[0] === "Playoff") aVal+=10000;
            if (bSplit[0] === "Playoff") bVal+=10000;

            if (aVal > bVal) return 1;
            if (aVal < bVal) return -1;
            return 0;
        }
        if (isNaN(aVal) || isNaN(bVal)){
            // console.log(sortCategory,"null");
            return aRaw.localeCompare(bRaw);
        }
        if (aVal > bVal) return 1;
        if (aVal < bVal) return -1;
        return 0;
    });

    if (descending){
        rows = rows.reverse();
    }

    table.append(...rows);
}

function download_table_as_csv(separator = ',') {
    var rows = table.querySelectorAll("tr");
    var csv = [];
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');
        for (var j = 0; j < cols.length; j++) {
            let cell = cols[j];
            let data = cell.textContent.trim().replace(/\s+/g, ' ');
            if (cell.dataset.type === "string"){
                data = data.replace(/"/g, '""');
                row.push('"' + data + '"');
            } else {
                row.push(""+data);
            }
        }
        csv.push(row.join(separator));
    }
    var csv_string = csv.join('\n');
    // Download it
    var filename = 'match_data_'+new Date().toLocaleDateString() + '.csv';
    var link = document.createElement('a');
    link.style.display = 'none';
    const url = URL.createObjectURL(new Blob([csv_string], {type: 'text/csv;charset=utf-8'}));
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

updateSort();