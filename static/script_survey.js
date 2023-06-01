let surveyId;

// Get the modal
let modal = document.getElementById("surveyDeletionModal");

// Get the <span> element that closes the modal
let span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
  surveyId = undefined;
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
    surveyId = undefined;
  }
}

function confirmSurveyDeletion(event) {
  modal.style.display = "block";
  surveyId = event.value;
}

function exitModal() {
  modal.style.display = "none";
  surveyId = undefined;
}