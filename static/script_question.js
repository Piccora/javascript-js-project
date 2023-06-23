let surveyId;
let questionId;
let questionType;

// Get the modal
let questionAdditionModal = document.getElementById("questionAdditionModal");
let questionDeletionModal = document.getElementById("questionDeletionModal");
let surveyShareConfirmation = document.getElementById("surveyShareConfirmation");
let surveyShareModal = document.getElementById("surveyShareModal");

// Get the <span> element that closes the modal
let spanAddition = document.getElementById("closeAddition");
let spanDeletion = document.getElementById("closeDeletion");
let spanShareConfirmation = document.getElementById("closeShareConfirmation");
let spanShare = document.getElementById("closeShare");

// When the user clicks on <span> (x), close the modal
spanAddition.onclick = function() {
    questionAdditionModal.style.display = "none";
    document.getElementById("questionArea").value = "";
    document.getElementById("dropdownQuestionButton").innerHTML = "Question Type";
    document.getElementById("buttonYes").style.display = "none";
    document.getElementById("buttonNo").style.display = "none";
    surveyId = undefined;
    renderQuestionStructure();
}

spanDeletion.onclick = function() {
    questionDeletionModal.style.display = "none";
    questionId = undefined;
}

spanShareConfirmation.onclick = function() {
    surveyShareConfirmation.style.display = "none";
    surveyId = undefined;
}

spanShare.onclick = function() {
    surveyShareModal.style.display = "none";
    surveyId = undefined;
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == questionAdditionModal || event.target == questionDeletionModal || event.target == surveyShareConfirmation || event.target == surveyShareModal) {
        questionDeletionModal.style.display = "none";
        questionAdditionModal.style.display = "none";
        surveyShareConfirmation.style.display = "none";
        surveyShareModal.style.display = "none";
        document.getElementById("questionArea").value = "";
        document.getElementById("dropdownQuestionButton").innerHTML = "Question Type";
        document.getElementById("buttonYes").style.display = "none";
        document.getElementById("buttonNo").style.display = "none";
        surveyId = undefined;
        questionId = undefined;
        renderQuestionStructure();
    }
}

// Display the confirm question deletion modal
function confirmQuestionDeletion(event) {
    questionDeletionModal.style.display = "block";
    questionId = event.getAttribute("value");
}

// Display the confirm question sharing modal
function confirmSurveySharing(event) {
    surveyShareConfirmation.style.display = "block";
    surveyId = event.getAttribute("value");
}

// Display the adding question modal
function renderQuestionModal(event) {
    questionAdditionModal.style.display = "block";
    surveyId = event.getAttribute("value");
}

// Universal function to hide every modal when a modal is closed
function exitModal() {
    questionDeletionModal.style.display = "none";
    questionAdditionModal.style.display = "none";
    surveyShareConfirmation.style.display = "none";
    document.getElementById("buttonYes").style.display = "none";
    document.getElementById("buttonNo").style.display = "none";
    document.getElementById("questionArea").value = "";
    document.getElementById("dropdownQuestionButton").innerHTML = "Question Type";
    renderQuestionStructure();
    surveyId = undefined;
}

// Function to replace the initial dropdown text when you click on a question type
function replaceDropdownText(event) {
    document.getElementById("dropdownQuestionButton").innerHTML = event.getAttribute("value");
}

// Function to render the corresponding question structure for the right question type
function renderQuestionStructure() {
    questionType = document.getElementById("dropdownQuestionButton").innerHTML;
    document.getElementById("questionChoices").innerHTML = ""
    if (questionType != "Question Type") {
        document.getElementById("buttonYes").style.display = "block";
        document.getElementById("buttonNo").style.display = "block";
    }
    if (questionType === "Multiple Choice Question") {
        document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer1" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer2" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer3" rows="1"></textarea>
    </div>
    `
    } else if (questionType === "Checkbox Question") {
        document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="checkbox" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer1" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer2" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" disabled>
      <textarea class="form-control" placeholder="Enter an answer here" id="answer3" rows="1"></textarea>
    </div>
    `
    } else if (questionType === "Open-ended Question") {
        document.getElementById("questionChoices").innerHTML += `
    <div class="form-group">
      <textarea class="form-control" id="exampleFormControlTextarea1" id="answer" rows="3" disabled></textarea>
    </div>
    `
    } else if (questionType === "Close-ended Question") {
        document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio" disabled>
      <label class="form-check-label">
        Yes
      </label>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" disabled>
      <label class="form-check-label">
        No
      </label>
    </div>
    `
    }
}

// Function to add a question
function addQuestion() {
    let questionTypeObject = {
        "Multiple Choice Question": "MCQ",
        "Checkbox Question": "Checkbox",
        "Open-ended Question": "Open-ended",
        "Close-ended Question": "Close-ended"
    };
    // Make an AJAX request based on the question type, if there's an error, render the apology page
    if (["Multiple Choice Question", "Checkbox Question"].includes(questionType)) {
        $.ajax({
            type: "POST",
            url: "/add-question",
            async: false,
            contentType: "application/json",
            data: JSON.stringify({
                question: document.getElementById("questionArea").value.trim(),
                question_type: questionTypeObject[questionType],
                survey_id: surveyId,
                answer1: document.getElementById("answer1").value.trim(),
                answer2: document.getElementById("answer2").value.trim(),
                answer3: document.getElementById("answer3").value.trim()
            }),
            success: function(response) {
                console.log("response: " + response["response"]);
                if (response["response"] === "success") {
                    location.reload();
                } else {
                    $("*").html(response["page"]);
                }
            }
        });
    } else if (["Open-ended Question", "Close-ended Question"]) {
        $.ajax({
            type: "POST",
            url: "/add-question",
            async: false,
            contentType: "application/json",
            data: JSON.stringify({
                question: document.getElementById("questionArea").value.trim(),
                question_type: questionTypeObject[questionType],
                survey_id: surveyId
            }),
            success: function(response) {
                console.log("response: " + response["response"]);
                if (response["response"] === "success") {
                    location.reload();
                } else {
                    $("*").html(response["page"]);
                }
            }
        });
    }
}

// Function to delete a specific question
function deleteQuestion() {
  // Make an AJAX request to delete the specified question
    $.ajax({
        type: "POST",
        url: "/delete-question",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({
            question_id: questionId
        }),
        success: function(response) {
            console.log("response: " + response["response"]);
            location.reload();
        }
    });
}

function shareSurvey() {
  // Make an AJAX request to get the survey code
    $.ajax({
        type: "POST",
        url: "/return-survey-code",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({
            survey_id: surveyId
        }),
        success: function(response) {
          // Display the modal containing the survey link, and also the survey code
            document.getElementById("survey_share").innerHTML = "";
            console.log("response: " + response["response"]);
            let survey_link = document.createElement("h3");
            let survey_code = document.createElement("h3");
            survey_link.innerHTML = `<h3>Here's the link to do the survey: https://portfolio-javascript-project.onrender.com/survey/${response["survey_code"]}</h3>`
            survey_code.innerHTML = `<h3>Or you can use this code in the "Do a survey" section: ${response["survey_code"]}</h3>`
            document.getElementById("survey_share").appendChild(survey_link);
            document.getElementById("survey_share").appendChild(survey_code);
            surveyShareConfirmation.style.display = "none";
            surveyShareModal.style.display = "block";
        }
    });
}