import os
import time
import certifi
import bcrypt

from flask import Flask, flash, redirect, render_template, request, session, make_response
from flask_session import Session
from tempfile import mkdtemp
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
client = MongoClient(os.getenv("CONNECTION"), server_api=ServerApi('1'))

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
        return render_template("survey-list.html", survey_list=list(survey_list.find({"user_id": session["user_id"]})))
    return render_template("welcome.html")

# @login_required
# def index():
#     print(list(survey_list.find({"user_id": session["user_id"]})))
#     return render_template("survey-list.html", survey_list=list(survey_list.find({"user_id": session["user_id"]})))

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
        user = dict(users.find_one({"username": request.form.get("username").strip()}))
        if not user or not bcrypt.checkpw(request.form.get("password").strip().encode("utf-8"), user["password"]):
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
        username_check = users.find_one({"username": request.form.get("username").strip()})
        if username_check:
            return apology("username is not available", 400)

        # # Ensure there's no duplicate email
        # email_check = users.find({"email": request.form.get("email").strip()})
        # for email in email_check:
        #     if request.form.get("email").strip() == email["email"]:
        #         return apology("email is not available", 400)

        # Insert username and password into database
        users.insert_one(
            {
                "_id": users.count_documents({}) + 1,
                "username": request.form.get("username").strip(),
                # "email": request.form.get("email").strip(),
                "password": bcrypt.hashpw(request.form.get("password").strip().encode("utf-8"), bcrypt.gensalt()),
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
    
@app.route("/render-questions/<survey_code>", methods=["GET", "POST"])
@login_required
def render_questions(survey_code=0):
    if request.method == "GET":
        return render_template("survey-questions.html", questions=list(survey_questions_and_answers.find({"survey_id": int(survey_code)})))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("login.html")

if __name__ == "__main__":
    app.run()