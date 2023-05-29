// function callRenderQuestions(id) {
//     console.log(id)
//     let response = $.ajax({
//         type: "POST",
//         url: "/render-questions",
//         async: false,
//         data: { surveyId: id }
//     });
    
//     return response.responseText;
// }

// const renderQuestions = document.querySelectorAll("#surveyName");
// renderQuestions.forEach(el => {
//     el.addEventListener("click", () => {
//         console.log(callRenderQuestions(el.getAttribute("value")))
//     })
// })

let surveyId;

// Get the modal
let modal = document.getElementById("myModal");

// Get the <span> element that closes the modal
let span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

function confirmSurveyDeletion(event) {
  modal.style.display = "block";
  surveyId = event.target.value;
}

function exitModal() {
  modal.style.display = "none";
  surveyId = None;
}

function replaceDropdownText(event) {
  document.getElementById("dropdownQuestionButton").innerHTML = event.innerHTML;
}

function renderQuestionStructure() {
  console.log("success")
  questionType = document.getElementById("dropdownQuestionButton").innerHTML;
  document.getElementById("questionChoices").innerHTML = ""
  if (questionType == "Multiple Choice Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    `
  } else if (questionType == "Checkbox Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="checkbox" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" value="" id="defaultCheck1">
      <textarea class="form-control" placeholder="Enter your answer here"></textarea>
    </div>
    `
  } else if (questionType == "Open-ended Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-group">
      <textarea class="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
    </div>
    `
  } else if (questionType == "Close-ended Question") {
    document.getElementById("questionChoices").innerHTML += `
    <div class="form-check">
      <input class="form-check-input" type="radio" name="exampleRadios" id="exampleRadios1" value="option1" checked>
      <label class="form-check-label" for="exampleRadios1">
        Yes
      </label>
    </div>
    <div class="form-check">
      <input class="form-check-input" type="radio" name="exampleRadios" id="exampleRadios2" value="option2">
      <label class="form-check-label" for="exampleRadios2">
        No
      </label>
    </div>
    `
  }
}

setInterval(renderQuestionStructure, 500);