const matchButton = document.getElementById("matchBtn")
const autoButton = document.getElementById("autoBtn")
const teleopButton = document.getElementById("teleopBtn")

const matchTab = document.getElementById("match")
const autoTab = document.getElementById("auto")
const teleopTab = document.getElementById("teleop")

function showMatch() {
    matchTab.style.display = 'inline';
    autoTab.style.display = 'none';
    telopTab.style.display = 'none';
}

function showAuto() {
    matchTab.style.display = 'none';
    autoTab.style.display = 'inline';
    telopTab.style.display = 'none';
}

function showTeleop() {
    matchTab.style.display = 'none';
    autoTab.style.display = 'none';
    telopTab.style.display = 'inline';
}
