import os
import bcrypt
import json
import string
import secrets

from flask import Flask, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from helpers import apology, login_required
from dotenv import load_dotenv

load_dotenv()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure application to use mongoDB database
client = MongoClient(os.getenv("CONNECTION"), server_api=ServerApi("1"))

# Configure session to use mongodb (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = client
app.config["SESSION_MONGODB_DB"] = "survey-database"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"
Session(app)

# Configuring database's collections
db = client["survey-database"]
users = db["user"]
survey_list = db["survey-list"]
survey_questions_and_answers = db["survey-questions-and-answers"]

@app.after_request
def after_request(response):
    """Ensure responses aren"t cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def welcome():
    """
    The welcome page of the web application, by default render the welcome.html page (the default homepage),
    but render the survey-list.html page (the user homepage) instead if there is a user session
    """
    if session.get("user_id") is not None:
        return render_template(
            "survey-list.html",
            survey_list=list(survey_list.find({"user_id": session["user_id"]})),
            user_id=session["user_id"],
            username=users.find_one({"_id": session["user_id"]})["username"],
        )
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username").strip():
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password").strip():
            return apology("must provide password", 403)

        # Check if user exists in the database. If so, compare their password
        user = users.find_one({"username": request.form.get("username").strip()})
        if not user or not bcrypt.checkpw(
            request.form.get("password").strip().encode("utf-8"), user["password"]
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user["_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username").strip():
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password").strip():
            return apology("missing password", 400)
        
        # Ensure password satisfied the requirements
        state, error_message = password_check(request.form.get("password").strip())

        if not state:
            return apology(error_message, 400)

        # Ensure the password confirm field is the same as the password field
        if (
            request.form.get("password").strip()
            != request.form.get("confirmation").strip()
        ):
            return apology("passwords don't match", 400)

        # Ensure there"s no duplicate username
        username_check = users.find_one(
            {"username": request.form.get("username").strip()}
        )
        if username_check:
            return apology("username is not available", 400)

        # Insert username and password into database
        users.insert_one(
            {
                "_id": users.count_documents({}) + 1,
                "username": request.form.get("username").strip(),
                "password": bcrypt.hashpw(
                    request.form.get("password").strip().encode("utf-8"),
                    bcrypt.gensalt(),
                ),
            }
        )

        # Remember which user has logged in
        session["user_id"] = users.find_one({"username": request.form.get("username").strip()})["_id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/render-questions/<survey_id>", methods=["GET", "POST"])
@login_required
def render_questions(survey_id=0):
    """
    Render questions for a particular survey. If the survey_id is not from the user, returns
    an error.
    """
    # User reached route via GET
    if request.method == "GET":

        # List of surveys that the user has
        authorized_surveys = [
            int(survey["_id"])
            for survey in list(survey_list.find({"user_id": session["user_id"]}))
        ]

        # Check if user is accessing an unauthorized survey
        if int(survey_id) not in authorized_surveys:
            return apology("unauthorized access to survey", 403)
        
        # Render the page with the questions
        return render_template(
            "survey-questions.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": int(survey_id)})
            ),
            survey_id=int(survey_id),
        )
    
    # User reached route via POST
    else:
        return redirect("/")


@app.route("/add-question", methods=["GET", "POST"])
@login_required
def add_question():
    # User reached route via POST
    if request.method == "POST":

        # Get the survey ID and the question type
        survey_id = json.loads(request.data).get("survey_id")
        question_type = json.loads(request.data).get("question_type")

        # Check if questions and answers are valid
        if not json.loads(request.data).get("question").strip():
            return jsonify({"response": "failure", "page": apology("empty question", 406)})

        # Check the question type and insert into the collection with the appropriate information
        if question_type == "MCQ" or question_type == "Checkbox":
            answer1, answer2, answer3 = (
                json.loads(request.data).get("answer1").strip(),
                json.loads(request.data).get("answer2").strip(),
                json.loads(request.data).get("answer3").strip(),
            )
            if not answer1 or not answer2 or not answer3:
                return jsonify({"response": "failure", "page": apology("one or more answers is empty", 406)})
            
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question").strip(),
                    "question_type": question_type,
                    "answers": {answer1: 0, answer2: 0, answer3: 0},
                }
            )
        elif question_type == "Open-ended":
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question").strip(),
                    "question_type": question_type,
                    "answers": [],
                }
            )
        elif question_type == "Close-ended":
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question").strip(),
                    "question_type": question_type,
                    "answers": {"Yes": 0, "No": 0},
                }
            )
        return jsonify({"response": "success"})
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/delete-question", methods=["GET", "POST"])
@login_required
def delete_question():
    """
    Delete user survey's question
    """

    # User reached route via POST
    if request.method == "POST":
        # Delete the specific question
        survey_questions_and_answers.delete_one(
            {"_id": int(json.loads(request.data).get("question_id"))}
        )
        return jsonify({"response": "success"})
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/add-survey", methods=["GET", "POST"])
@login_required
def add_survey():
    """
    Add a survey with the survey's name when the user requests to do so
    """

    # User reached route via POST
    if request.method == "POST":

        if not json.loads(request.data).get("question").strip():
            return jsonify({"response": "failure", "page": apology("empty survey name", 406)})

        # While true loop to generate a unique code attached to that survey (use when the user wants to share the survey)
        while True:
            survey_code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )

            # Condition to check if the randomly generated code hasn't existed in the collection yet. If it is, generate the code again
            if survey_list.find_one({"survey_code": survey_code}) is None:
                break

        # Insert the survey's information into the collection
        survey_list.insert_one(
            {
                "_id": survey_list.count_documents({}) + 1,
                "user_id": int(session["user_id"]),
                "survey_name": json.loads(request.data).get("question").strip(),
                "survey_code": survey_code,
            }
        )
        return jsonify({"response": "success"})
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/delete-survey", methods=["GET", "POST"])
@login_required
def delete_survey():
    """
    Delete the survey through the survey's ID, as well as deleting the questions inside that survey
    """

    # User reached route via POST
    if request.method == "POST":
        # Get the survey id, delete the id and the corresponding questions with it
        survey_id = int(json.loads(request.data).get("survey_id"))
        survey_list.delete_one({"_id": survey_id, "user_id": int(session["user_id"])})
        survey_questions_and_answers.delete_many({"survey_id": survey_id})
        return jsonify({"response": "success"})
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/survey", methods=["GET", "POST"])
@app.route("/survey/", methods=["GET", "POST"])
@app.route("/survey/<survey_code>", methods=["GET", "POST"])
def survey(survey_code=None):
    """
    Render survey for users to do, if the survey code is none then redirect them to another
    page to fill in the survey code
    """

    # User reached route via GET
    if request.method == "GET":
        # Check for survey code
        if survey_code is None:
            return render_template("input-code.html")
        survey = survey_list.find_one({"survey_code": survey_code})
        # Check if survey exists
        if survey is None:
            return apology("survey doesn't exist", 404)
        
        # Render the survey
        return render_template(
            "render-survey.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": survey["_id"]})
            ),
            survey_code=survey_code,
        )
    
    # User reached route via POST
    else:
        # Check if survey code exists
        if survey_code is None:
            return redirect(
                url_for("survey", survey_code=str(request.form.get("survey_code")))
            )
        survey = survey_list.find_one({"survey_code": survey_code})

        # Return apology if survey doesn't exist
        if survey is None:
            return apology("survey doesn't exist", 404)
        survey_id = survey["_id"]
        question_id_list = [
            question["_id"]
            for question in list(
                survey_questions_and_answers.find({"survey_id": survey_id})
            )
        ]

        # Update the answers of the survey based on the survey-doer answers
        for question_id in question_id_list:
            question_type = survey_questions_and_answers.find_one({"_id": question_id})[
                "question_type"
            ]
            if question_type == "MCQ" or question_type == "Close-ended":
                answer = request.form.get("question" + str(question_id))
                if answer is not None:
                    survey_questions_and_answers.update_one(
                        {"_id": question_id}, {"$inc": {"answers.{}".format(answer): 1}}
                    )
            elif question_type == "Checkbox":
                answers = request.form.getlist("question" + str(question_id))
                for answer in answers:
                    survey_questions_and_answers.update_one(
                        {"_id": question_id}, {"$inc": {"answers.{}".format(answer): 1}}
                    )
            elif question_type == "Open-ended":
                answer = request.form.get("question" + str(question_id)).strip()
                if answer:
                    survey_questions_and_answers.update_one(
                        {"_id": question_id}, {"$push": {"answers": answer}}
                    )
        return render_template("survey-completion.html")


@app.route("/return-survey-code", methods=["GET", "POST"])
@login_required
def return_code():
    """Return a specific survey's code"""

    # User reached route via POST
    if request.method == "POST":
        # Return the corresponding survey code
        return jsonify(
            {
                "survey_code": survey_list.find_one(
                    {"_id": int(json.loads(request.data).get("survey_id"))}
                )["survey_code"],   
                "response": "success",
            }
        )
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/survey-analytic/<survey_id>", methods=["GET", "POST"])
@login_required
def survey_analytic(survey_id=0):
    """Render the survey analytic page"""

    # User reached route via GET
    if request.method == "GET":
        # Get the authorized surveys that the user has
        authorized_surveys = [
            int(survey["_id"])
            for survey in list(survey_list.find({"user_id": session["user_id"]}))
        ]

        # Check if the user is accessing the authorized survey
        if int(survey_id) not in authorized_surveys:
            return apology("unauthorized access to survey", 403)
        
        # Render the survey analytic page
        return render_template(
            "survey-analytic.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": int(survey_id)})
            ),
            survey_id=survey_id,
        )
    
    # User reached route via POST
    else:
        return redirect("/")


@app.route("/render-charts", methods=["GET", "POST"])
@login_required
def render_charts():
    """Return the rendered charts"""

    # User reached route via POST
    if request.method == "POST":
        
        # Return the charts to render to the web application
        return jsonify(
            {
                "survey_questions_and_answers": list(
                    survey_questions_and_answers.find(
                        {"survey_id": int(json.loads(request.data).get("survey_id"))}
                    )
                ),
                "response": "success",
            }
        )
    
    # User reached route via GET
    else:
        return redirect("/")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log out your account"""
    session.clear()
    return redirect("/")


@app.route("/<first>")
@app.route("/<first>/")
@app.route("/<first>/<path:rest>")
def fallback(first=None, rest=None):
    """Other routes that don't exist will return an apology"""
    return apology("that route doesn't exist", 404)


def password_check(password):
    """
    Password check function with the following requirements:\n
    - At least 8 characters\n
    - At least one digit\n
    - At least one uppercase character\n
    - At least one lowercase character\n
    - At least one special character ($, @, #, %)
    """
    symbols =["$", "@", "#", "%"]
    if len(password) < 8:
        return False, "password length is too short"
 
    # Check if password contains at least one digit, uppercase letter, lowercase letter, and special symbol

    # A dictionary representing whether the requirements are fulfilled, in the following order:
    # - Password has at least one digit
    # - Password has at least one uppercase character
    # - Password has at least one lowercase character
    # - Password has at least one special character
    requirements = {"has_digit": False, "has_uppercase_character": False, "has_lowercase_character": False, "has_symbol": False}

    for char in password:
        if ord(char) in range(48, 58):
            requirements["has_digit"] = True
        elif ord(char) in range(65, 91):
            requirements["has_uppercase_character"] = True
        elif ord(char) in range(97, 123):
            requirements["has_lowercase_character"] = True
        elif char in symbols:
            requirements["has_symbol"] = True

    if not requirements["has_digit"]:
        return False, "Password should have at least one numeral"
    if not requirements["has_uppercase_character"]:
        return False, "Password should have at least one uppercase letter"
    if not requirements["has_lowercase_character"]:
        return False, "Password should have at least one lowercase letter"
    if not requirements["has_symbol"]:
        return False, "Password should have at least one of the symbols $@#%"

    return True, ""


if __name__ == "__main__":
    app.run()
