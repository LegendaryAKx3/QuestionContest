from functools import wraps

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

app = Flask(__name__)

#Initialize DB
db = SQL("sqlite:///contest.db")

# Initialize session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uuid") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

@app.route("/")
@login_required
def index():
    leaderboard = db.execute("select * from accounts order by questions desc limit 10;")
    for i in range(len(leaderboard)):
        leaderboard[i]["rank"] = i + 1
    questions = db.execute("select * from accounts where id = ?;", session["uuid"])[0]["questions"]
    return render_template("index.html", leaderboard=leaderboard, questions = questions)

@app.route("/add", methods=["POST"])
@login_required
def add():
    # Add an inputted number of questions to the users question count
    inputted = request.form.get("add")
    if int(inputted) > 20:
        flash("Try not to add too many questions at once")
    else:
        user_questions = db.execute("select * from accounts where id = ?;", session["uuid"])[0]["questions"]
        db.execute("update accounts set questions = ? where id = ?;", int(user_questions) + int(inputted), session["uuid"])
    return redirect("/")

@app.route("/subtract", methods=["POST"])
def subtract():
    # Remove an inputted number of questions from the user's question count
    inputted = request.form.get("subtract")
    user_questions = db.execute("select * from accounts where id = ?;", session["uuid"])[0]["questions"]
    db.execute("update accounts set questions = ? where id = ?;", int(user_questions) - int(inputted), session["uuid"])
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check both username and password are submitted
        if (not request.form.get("username")) or (not request.form.get("password")):
            flash("Please enter both username and password")
            return render_template(
                "login.html"
            )

        user = db.execute(
            "SELECT * FROM accounts WHERE username = ?", request.form.get("username")
        )
        # Ensure username exists and password is correct

        # HACK: len(user) != 1?
        if len(user) != 1 or not check_password_hash(
            user[0]["hash"], request.form.get("password")
        ):
            flash("Invalid login information")
            return render_template("login.html")

        # store account login status until session is cleared
        session["uuid"] = user[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user (Personal code from CS50 Finance)"""
    if request.method == "POST":
        # get form info and check validity

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Username field cannot be empty")
            return render_template(
                "register.html"
            )

        for entry in db.execute("SELECT username FROM accounts;"):
            if username == entry["username"]:
                flash("Username is Already Taken")
                return render_template(
                    "register.html"
                )

        # check password valididty
        if password != confirmation or (not password) or (not confirmation):
            flash("Invalid password or confirmation")
            return render_template(
                "register.html"
            )

        elif (len(password) < 8) or (password.lower() == password):
            flash("Password Must be at Least 8 Characters Long and Contain a Capital Letter")
            return render_template(
                "register.html"
            )

        db.execute(
            "INSERT INTO accounts (username, hash, questions) VALUES(?, ?, ?);",
            username,
            generate_password_hash(password),
            0
        )
        return redirect("/")
    return render_template("register.html")