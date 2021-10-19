from flask import Flask, request, render_template, url_for, redirect, make_response, Response
import requests
from models import User, Messages,  db
import hashlib
import uuid
import os
from sqlalchemy import desc

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
    response = make_response(redirect(url_for("profile")))
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
    receiver = db.query(User).get(int(user_id))

    session_token = request.cookies.get("session_token")

    sender = db.query(User).filter_by(session_token=session_token).first()

    return render_template("user_details.html", receiver=receiver, sender=sender)



@app.route("/successfully_sent", methods=["POST"])
def successfully_sent():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()


    if user:
        receiver = request.form.get("send_to")
        text = request.form.get("text")
        sender = user.email
        

        messages = Messages(sender=sender, receiver=receiver, text=text)
        messages.save()


        return redirect(url_for("successfully_sent_message"))


    else:
        return "Try again."


@app.route("/successfully_sent_message", methods=["GET"])
def successfully_sent_message():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()
    sender = user.email

    messages = db.query(Messages).filter_by(sender=sender).first()
    #dokwončej mona
    
    
    return render_template("success_message.html", messages=messages)




@app.route("/sent_messages")
def sent_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    sender = user.email

    messages = db.query(Messages).filter_by(sender=sender)

 
    return render_template("sent_messages.html", messages=messages)


@app.route("/received_messages")
def received_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    receiver = user.email

    messages = db.query(Messages).filter_by(receiver=receiver)

 
    return render_template("received_messages.html", messages=messages)







try:
    import secrets
except ImportError as e:
    pass

@app.route("/weather", methods=["GET"])
def weather():
    query = "Ljubljana,SLO"
    unit="metric"
    api_key = os.environ.get("API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units={1}&appid={2}".format(query, unit, api_key)
    data = requests.get(url=url)

    return render_template("weather.html", data=data.json())



@app.route("/index", methods=["GET"])
def clear():
    resp = make_response(render_template("index.html"))
    resp.set_cookie("session_token", expires=0)

    return resp


if __name__=="__main__":
    app.run()

