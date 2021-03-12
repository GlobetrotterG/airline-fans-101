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
def shares():
    shares = list(mongo.db.shares.find())
    return render_template("share.html", shares=shares)


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
        return redirect(url_for("profile", username=session["airlinefan"]))
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
                    return redirect(url_for(
                        "profile", username=session["airlinefan"]))
            else:
                flash("Please return to the Boarding Gate! Incorrect Username and/or Password")
                return redirect(url_for("login"))

       else: 
            flash("Please return to the Boarding Gate! Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.fan_users.find_one(
        {"username": session["airlinefan"]})["username"]
    
    if session["airlinefan"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("We've landed! You are now logged out")
    session.pop("airlinefan")
    return redirect(url_for("login"))


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        share = {
                "category_name": request.form.get("category_name"),
                "airline_name": request.form.get("airline_name"),
                "airline_class": request.form.get("airline_class"),
                "destination": request.form.get("destination"),
                "review": request.form.get("review"),
                "airline_reviewer": session["airlinefan"]
        }
        mongo.db.shares.insert_one(share)
        flash("Your Review is Successfully Added from 33,000 Feet")
        return redirect(url_for("shares"))

    return render_template("add_review.html")


@app.route("/edit_review/<share_id>", methods=["GET", "POST"])
def edit_review(share_id):
    if request.method == "POST":
        sending = {
                "category_name": request.form.get("category_name"),
                "airline_name": request.form.get("airline_name"),
                "airline_class": request.form.get("airline_class"),
                "destination": request.form.get("destination"),
                "review": request.form.get("review"),
                "airline_reviewer": session["airlinefan"]
        }
        mongo.db.shares.update({"_id": ObjectId(share_id)}, sending)
        flash("Your Review is Successfully Updated. Please Fasten your Seatbelt!")

    share = mongo.db.shares.find_one({"_id": ObjectId(share_id)})
    return render_template("edit_review.html", share=share)


@app.route("/delete_review/<share_id>")
def delete_review(share_id):
    mongo.db.shares.remove({"_id": ObjectId(share_id)})
    flash("Review is now Deleted. Would you like Tea of Coffee?")
    return redirect(url_for("shares"))



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
