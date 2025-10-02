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

function downloadScore(robotNum,matchNum,compLevel,setNum,data){
    fullData = {
        "robotNum":robotNum,
        "matchNum":matchNum,
        "compLevel":compLevel,
        "setNum":setNum,
        "data":data
    };

    download(JSON.stringify(fullData),"score-"+robotNum+"-"+compLevel+"-"+matchNum+"-"+setNum,"application/json");
}