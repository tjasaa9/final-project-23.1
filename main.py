from flask import Flask, request, render_template, url_for, redirect, make_response, Response
from models import User, db
import hashlib
import uuid

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None
    return render_template("index.html", user=user)




@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    #see if user already exists
    user = db.query(User).filter_by(email=email).first()
    
    #if the user doesn't exist yet, create a User object
    if not user:
        user = User(email=email, password=hashed_password)
        user.save()
    
    #check if the user's password is incorrect
    if hashed_password != user.password:
        return "Wrong password. Try again"
    #else if the user's password is correct, create a session token for this user
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())
    
    #save user's session_token in a db
    user.session_token = session_token
    user.save()
    
    
    #save user's session into a cookie
    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")
    
    return response


@app.route("/profile", methods =["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    #search for user in the database
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).all()

    return render_template("users.html", users=users)


@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)


@app.route("/send_message", methods=["GET"])
def send_message():


    return render_template("send_message.html")


@app.route("/successfully_sent", methods=["POST"])
def successfully_sent():

    

    return "Successfully sent!"

if __name__=="__main__":
    app.run(debug=True)
