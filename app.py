import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/shares")
def shares():
    share = mongo.db.shares.find()
    return render_template("share.html", share=share)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        current_user = mongo.db.fan_users.find_one(
            {"username": request.form.get("username").lower()})

        if current_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.fan_users.insert_one(register)

        session["airlinefan"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
       current_user = mongo.db.fan_users.find_one(
           {"username": request.form.get("username").lower()})

       if current_user:
            if check_password_hash(
                current_user["password"], request.form.get("password")):
                    session["airlinefan"] = request.form.get("username").lower()
                    flash("Welcome Aboard Airline Fans 101, {}!".format(
                        request.form.get("username")))
            else:
                flash("Please return to the Boarding Gate! Incorrect Username and/or Password")
                return redirect(url_for("login"))

       else: 
            flash("Please return to the Boarding Gate! Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
