import os
import time
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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure application to use mongoDB database
client = MongoClient(os.getenv("CONNECTION"), server_api=ServerApi("1"))

db = client["survey-database"]
users = db["user"]
survey_list = db["survey-list"]
survey_questions_and_answers = db["survey-questions-and-answers"]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def welcome():
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
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
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
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("missing password", 400)

        # Ensure the password confirm field is the same as the password field
        if (
            request.form.get("password").strip()
            != request.form.get("confirmation").strip()
        ):
            return apology("passwords don't match", 400)

        # Ensure there's no duplicate username
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

        time.sleep(5)

        # Remember which user has logged in
        session["user_id"] = list(
            users.find({"username": request.form.get("username").strip()})
        )[0]["_id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/render-questions/<survey_id>", methods=["GET", "POST"])
@login_required
def render_questions(survey_id=0):
    if request.method == "GET":
        authorized_surveys = [
            int(survey["_id"])
            for survey in list(survey_list.find({"user_id": session["user_id"]}))
        ]
        if int(survey_id) not in authorized_surveys:
            return apology("unauthorized access to survey", 403)
        return render_template(
            "survey-questions.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": int(survey_id)})
            ),
            survey_id=int(survey_id),
        )
    else:
        return redirect("/")


@app.route("/add-question", methods=["GET", "POST"])
@login_required
def add_question():
    if request.method == "POST":
        survey_id = json.loads(request.data).get("survey_id")
        question_type = json.loads(request.data).get("question_type")
        if question_type == "MCQ" or question_type == "Checkbox":
            answer1, answer2, answer3 = (
                json.loads(request.data).get("answer1"),
                json.loads(request.data).get("answer2"),
                json.loads(request.data).get("answer3"),
            )
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question"),
                    "question_type": question_type,
                    "answers": {answer1: 0, answer2: 0, answer3: 0},
                }
            )
        elif question_type == "Open-ended":
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question"),
                    "question_type": question_type,
                    "answers": [],
                }
            )
        elif question_type == "Close-ended":
            survey_questions_and_answers.insert_one(
                {
                    "_id": survey_questions_and_answers.count_documents({}) + 1,
                    "survey_id": int(survey_id),
                    "question": json.loads(request.data).get("question"),
                    "question_type": question_type,
                    "answers": {"Yes": 0, "No": 0},
                }
            )
        return jsonify({"response": "success"})
    else:
        return redirect("/")


@app.route("/delete-question", methods=["GET", "POST"])
@login_required
def delete_question():
    if request.method == "POST":
        survey_questions_and_answers.delete_one(
            {"_id": int(json.loads(request.data).get("question_id"))}
        )
        return jsonify({"response": "success"})
    else:
        return redirect("/")


@app.route("/add-survey", methods=["GET", "POST"])
@login_required
def add_survey():
    if request.method == "POST":
        while True:
            survey_code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )
            if survey_list.find_one({"survey_code": survey_code}) is None:
                break
        survey_list.insert_one(
            {
                "_id": survey_list.count_documents({}) + 1,
                "user_id": int(session["user_id"]),
                "survey_name": json.loads(request.data).get("question"),
                "survey_code": survey_code,
            }
        )
        return jsonify({"response": "success"})
    else:
        return redirect("/")


@app.route("/delete-survey", methods=["GET", "POST"])
@login_required
def delete_survey():
    global authorized_surveys
    if request.method == "POST":
        survey_id = int(json.loads(request.data).get("survey_id"))
        survey_list.delete_one({"_id": survey_id, "user_id": int(session["user_id"])})
        survey_questions_and_answers.delete_many({"survey_id": survey_id})
        authorized_surveys = [
            int(survey["_id"])
            for survey in list(survey_list.find({"user_id": session["user_id"]}))
        ]
        return jsonify({"response": "success"})
    else:
        return redirect("/")


@app.route("/survey", methods=["GET", "POST"])
@app.route("/survey/<survey_code>", methods=["GET", "POST"])
def survey(survey_code=None):
    if request.method == "GET":
        if survey_code is None:
            return render_template("input-code.html")
        survey = survey_list.find_one({"survey_code": survey_code})
        if survey is None:
            return apology("survey doesn't exist", 404)
        return render_template(
            "render-survey.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": survey["_id"]})
            ),
            survey_code=survey_code,
        )
    else:
        if survey_code is None:
            return redirect(
                url_for("survey", survey_code=str(request.form.get("survey_code")))
            )
        survey = survey_list.find_one({"survey_code": survey_code})
        if survey is None:
            return apology("survey doesn't exist", 404)
        survey_id = survey["_id"]
        question_id_list = [
            question["_id"]
            for question in list(
                survey_questions_and_answers.find({"survey_id": survey_id})
            )
        ]
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
                answer = request.form.get("question" + str(question_id))
                if answer.strip() != "":
                    survey_questions_and_answers.update_one(
                        {"_id": question_id}, {"$push": {"answers": answer}}
                    )
        return render_template("survey-completion.html")


@app.route("/return-survey-code", methods=["GET", "POST"])
@login_required
def return_code():
    if request.method == "POST":
        return jsonify(
            {
                "survey_code": survey_list.find_one(
                    {"_id": int(json.loads(request.data).get("survey_id"))}
                )["survey_code"],
                "response": "success",
            }
        )
    else:
        return redirect("/")


@app.route("/survey-analytic/<survey_id>", methods=["GET", "POST"])
@login_required
def survey_analytic(survey_id=0):
    if request.method == "GET":
        authorized_surveys = [
            int(survey["_id"])
            for survey in list(survey_list.find({"user_id": session["user_id"]}))
        ]
        if int(survey_id) not in authorized_surveys:
            return apology("unauthorized access to survey", 403)
        return render_template(
            "survey-analytic.html",
            questions=list(
                survey_questions_and_answers.find({"survey_id": int(survey_id)})
            ),
            survey_id=survey_id,
        )
    else:
        return redirect("/")


@app.route("/render-charts", methods=["GET", "POST"])
@login_required
def render_charts():
    if request.method == "POST":
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
    else:
        return redirect("/")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
