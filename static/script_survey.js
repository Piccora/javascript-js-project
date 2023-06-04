let surveyId;
let userId;

// Get the modal
let surveyDeletionModal = document.getElementById("surveyDeletionModal");
let surveyAdditionModal = document.getElementById("surveyAdditionModal");

// Get the <span> element that closes the modal
let spanDeletion = document.getElementById("closeDeletion");
let spanAddition = document.getElementById("closeAddition");

// When the user clicks on <span> (x), close the modal
spanDeletion.onclick = function() {
  surveyAdditionModal.style.display = "none";
  surveyDeletionModal.style.display = "none";
  surveyId = undefined;
}

spanAddition.onclick = function() {
  surveyAdditionModal.style.display = "none";
  surveyDeletionModal.style.display = "none";
  surveyId = undefined;
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == surveyDeletionModal || event.target == surveyAdditionModal) {
    surveyAdditionModal.style.display = "none";
    surveyDeletionModal.style.display = "none";
    surveyId = undefined;
  }
}

function confirmSurveyDeletion(event) {
  surveyDeletionModal.style.display = "block";
  surveyId = event.value;
}

function confirmSurveyAddition(event) {
  surveyAdditionModal.style.display = "block";
  userId = event.getAttribute("value");
}

function exitModal() {
  surveyDeletionModal.style.display = "none";
  surveyId = undefined;
}

function deleteSurvey() {
  $.ajax({
    type: "POST",
    url: "/delete-survey",
    async: false,
    contentType: "application/json",
    data: JSON.stringify({ survey_id: surveyId }),
    success: function(response) {
      console.log("response: " + response["response"]);
      location.reload();
    }
  })
}

function addSurvey() {
  $.ajax({
    type: "POST",
    url: "/add-survey",
    async: false,
    contentType: "application/json",
    data: JSON.stringify({ question: document.getElementById("question").value }),
    success: function(response) {
      console.log("response: " + response["response"]);
      location.reload();
    }
  })
}