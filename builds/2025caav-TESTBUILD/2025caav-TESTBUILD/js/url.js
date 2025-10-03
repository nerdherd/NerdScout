var url = new URL(window.location.href);
if (url.searchParams.has("matchNum")){
    document.getElementById("matchNumInput").value = url.searchParams.get("matchNum");
};
if (url.searchParams.has("setNum")){
    document.getElementById("setNumInput").value = url.searchParams.get("setNum");
};
if (url.searchParams.has("compLevel")){
    document.getElementById("compLevelInput").value = url.searchParams.get("compLevel");
};
if (url.searchParams.has("station")){
    document.getElementById("sectionInput").value = url.searchParams.get("station");
};