let barColors = ["#EC6B56", "#FFC154", "#47B39C"]

function getQuestions() {
  `The function to get the questions, then display them on the survey analytic page.`
  // Make an AJAX request
    $.ajax({
        type: "POST",
        url: "/render-charts",
        async: false,
        contentType: "application/json",
        data: JSON.stringify({
            survey_id: document.getElementById("survey_return").getAttribute("value")
        }),
        success: function(response) {
            console.log("response: " + response["response"]);
            // Get each question, determine the question type, then render the chart based on the question type
            let surveyQuestionsAndAnswers = response["survey_questions_and_answers"];
            let questionType;
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
        }
    });
}

getQuestions();