// https://stackoverflow.com/questions/13405129/create-and-save-a-file-with-javascript

// Function to download data to a file
function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}

function downloadScore(section,matchNum,compLevel,setNum,data){
    fullData = {
        "station":section,
        "matchNum":matchNum,
        "compLevel":compLevel,
        "setNum":setNum,
        "data":data
    };

    alert("Please save the file to a location you will remember")
    download(JSON.stringify(fullData),"score"+"-"+compLevel+"-"+matchNum+"-"+setNum+"-"+section,"application/json");
}