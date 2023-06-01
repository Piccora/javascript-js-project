let surveyId;
let questionId;
let questionType;

// Get the modal
let questionAdditionModal = document.getElementById("questionAdditionModal");
let questionDeletionModal = document.getElementById("questionDeletionModal");

// Get the <span> element that closes the modal
let spanAddition = document.getElementById("closeAddition");
let spanDeletion = document.getElementById("closeDeletion");

// When the user clicks on <span> (x), close the modal
spanAddition.onclick = function() {
  questionAdditionModal.style.display = "none";
  document.getElementById("questionArea").value = "";
  document.getElementById("dropdownQuestionButton").innerHTML = "Dropdown button";
  document.getElementById("buttonYes").style.display = "none";
  document.getElementById("buttonNo").style.display = "none";
  surveyId = undefined;
  renderQuestionStructure();
}

spanDeletion.onclick = function() {
  questionDeletionModal.style.display = "none";
  document.getElementById("buttonYes").style.display = "none";
  document.getElementById("buttonNo").style.display = "none";
  surveyId = undefined;
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == questionAdditionModal || event.target == questionDeletionModal) {
    questionDeletionModal.style.display = "none";
    questionAdditionModal.style.display = "none";
    document.getElementById("questionArea").value = "";
    document.getElementById("dropdownQuestionButton").innerHTML = "Dropdown button";
    document.getElementById("buttonYes").style.display = "none";
    document.getElementById("buttonNo").style.display = "none";
    surveyId = undefined;
    renderQuestionStructure();
  }
}

function confirmQuestionDeletion(event) {
    questionDeletionModal.style.display = "block";
    questionId = event.getAttribute("value");
}

function renderQuestionModal(event) {
  questionAdditionModal.style.display = "block";
  surveyId = event.getAttribute("value");
}

function exitModal() {
  questionDeletionModal.style.display = "none";
  questionAdditionModal.style.display = "none";
  document.getElementById("buttonYes").style.display = "none";
  document.getElementById("buttonNo").style.display = "none";
  document.getElementById("questionArea").value = "";
  document.getElementById("dropdownQuestionButton").innerHTML = "Dropdown button";
  renderQuestionStructure();
  surveyId = undefined;
}

function replaceDropdownText(event) {
  document.getElementById("dropdownQuestionButton").innerHTML = event.getAttribute("value");
}

function renderQuestionStructure() {
  questionType = document.getElementById("dropdownQuestionButton").innerHTML;
  document.getElementById("questionChoices").innerHTML = ""
  if (questionType == "Multiple Choice Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer1" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer2" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer3" rows="1"></textarea>
    </div>
    `
    document.getElementById("buttonYes").style.display = "block";
    document.getElementById("buttonNo").style.display = "block";
  } else if (questionType == "Checkbox Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="checkbox">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer1" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer2" rows="1"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox">
      <textarea class="form-control" placeholder="Enter an answer here" id="answer3" rows="1"></textarea>
    </div>
    `
    document.getElementById("buttonYes").style.display = "block";
    document.getElementById("buttonNo").style.display = "block";
  } else if (questionType == "Open-ended Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-group">
      <textarea class="form-control" id="exampleFormControlTextarea1" id="answer" rows="3"></textarea>
    </div>
    `
    document.getElementById("buttonYes").style.display = "block";
    document.getElementById("buttonNo").style.display = "block";
  } else if (questionType == "Close-ended Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio" value="option1">
      <label class="form-check-label">
        Yes
      </label>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" value="option2">
      <label class="form-check-label">
        No
      </label>
    </div>
    `
    document.getElementById("buttonYes").style.display = "block";
    document.getElementById("buttonNo").style.display = "block";
  }
  
}

function addQuestion() {
  if (questionType == "Multiple Choice Question") {
    $.ajax({
      type: "POST",
      url: "/add-question",
      async: false,
      contentType: "application/json",
      data: JSON.stringify({ question: document.getElementById("questionArea").value,
              question_type: "MCQ",
              survey_id: surveyId,
              answer1: document.getElementById("answer1").value,
              answer2: document.getElementById("answer2").value,
              answer3: document.getElementById("answer3").value }),
      success: function(response) {
        console.log(response);
        location.reload();
      }});
  } else if (questionType == "Checkbox Question") {
    $.ajax({
      type: "POST",
      url: "/add-question",
      async: false,
      contentType: "application/json",
      data: JSON.stringify({ question: document.getElementById("questionArea").value,
              question_type: "Checkbox",
              survey_id: surveyId,
              answer1: document.getElementById("answer1").value,
              answer2: document.getElementById("answer2").value,
              answer3: document.getElementById("answer3").value }),
      success: function(response) {
        console.log(response);
        location.reload();
      }});
  } else if (questionType == "Open-ended Question") {
    $.ajax({
      type: "POST",
      url: "/add-question",
      async: false,
      contentType: "application/json",
      data: JSON.stringify({ question: document.getElementById("questionArea").value,
              question_type: "Open-ended",
              survey_id: surveyId }),
      success: function(response) {
        console.log(response);
        location.reload();
      }});
  } else if (questionType == "Close-ended Question") {
    $.ajax({
      type: "POST",
      url: "/add-question",
      async: false,
      contentType: "application/json",
      data: JSON.stringify({ question: document.getElementById("questionArea").value,
              question_type: "Close-ended",
              survey_id: surveyId }),
      success: function(response) {
        console.log(response);
        location.reload();
      }});
  }
}

function deleteQuestion() {
  $.ajax({
    type: "POST",
    url: "/delete-question",
    async: false,
    contentType: "application/json",
    data: JSON.stringify({ question_id: questionId }),
    success: function(response) {
      console.log(response);
      location.reload();
    }});
}
// TODO: Refactor code