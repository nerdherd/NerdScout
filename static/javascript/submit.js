
// function submitData(tMatchNum, tCompLevel, tSetNum, tRobot){

//     matchNum = tMatchNum
//     compLevel = tCompLevel
//     setNum = tSetNum
//     robot = tRobot


//     let startPos = 4-startPosSlider.value;
//     autoLeave = leaveCheck.checked;

//     autoProcessor = procNetVars[0] 
//     teleProcessor = procNetVars[1]
//     autoNet = procNetVars[2] 
//     teleNet = procNetVars[3]

//     const endPosWin = !(document.getElementById("attemptEP").checked);

//     attemptedEndPos = endPosDDown.value-1;

//     // if(endPosWin){
//     //     endPos = endPosDDown.value-1
//     // } else {
//     //     endPos = 1; // assume they parked
//     // }

//     cannedComments = []

//     for (const button of document.querySelectorAll(".canned-button.active")){
//         cannedComments.push(button.dataset.text);
//     }

//     comment = document.getElementById("comments").value

//     autoReefMiss = missVals[0];
//     autoProcessorMiss = missVals[1];
//     autoNetMiss = missVals[2];

//     teleReefMiss = missVals[3];
//     teleProcessorMiss = missVals[4];
//     teleNetMiss = missVals[5];


//     rawData = {
//         "preloadFuel":preloadFuel,
//         "auto
//     };
//     data = JSON.stringify(rawData)
//     fetch(window.location.href, {
//     method: "POST",
//     body: data, 
//     headers: {
//         "Content-type": "application/json; charset=UTF-8"
//     }
//     }).then(response =>{
//         if (response.ok){
//             alert("Succesfully submitted")
//             redirect_to_match()
//         } else{
//             alert("There was an error submitting.");
//         }
//     });;
// }