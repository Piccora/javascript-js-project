let barColors = ["#EC6B56", "#FFC154", "#47B39C"]

function getQuestions() {
  $.ajax({
    type: "POST",
    url: "/render-charts",
    async: false,
    contentType: "application/json",
    data: JSON.stringify({ survey_id: document.getElementById("survey_return").getAttribute("value") }),
    success: function(response) {
      console.log(response["response"]);
      surveyQuestionsAndAnswers = response["survey_questions_and_answers"]
      surveyQuestionsAndAnswers.forEach(element => {
        questionType = element["question_type"]
        if (["MCQ", "Checkbox"].includes(questionType)) {
          new Chart(`chart${element["_id"]}`, {
            type: "doughnut",
            data: {
              labels: Object.keys(element["answers"]),
              datasets: [{
                backgroundColor: barColors,
                data: Object.values(element["answers"])
              }]
            }
          });
        } else if (questionType === "Close-ended") {
          new Chart(`chart${element["_id"]}`, {
            type: "pie",
            data: {
              labels: Object.keys(element["answers"]),
              datasets: [{
                backgroundColor: barColors,
                data: Object.values(element["answers"])
              }]
            }
          });
        }
      });
    }});
}

getQuestions();