import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination, get_page_args, get_page_parameter

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Landing page/Login & Register Modal:
@app.route("/")
@app.route("/landing")
def landing():
    return render_template("index.html")


# Get Games
@app.route("/get_games")
def get_games():
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page',
        offset_parameter='offset')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 9
    offset = (page - 1) * per_page
    total = mongo.db.games.find().count()
    games = mongo.db.games.find({}, {"photo1": 1})
    games_paginated = games[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, 
        total=total, css_framework='boostrap5')
    return render_template("home.html", games=games_paginated, username="", 
    page=page, per_page= per_page, pagination=pagination)


# Search
@app.route("/search", methods=["GET", "POST"])
def search():
    query= request.form.get("query")
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page',
        offset_parameter='offset')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 9
    offset = (page - 1) * per_page
    total = mongo.db.games.find({"$text": {"$search": query}}).count()
    games = mongo.db.games.find({"$text": {"$search": query}}, {"photo1"})
    games_paginated = games[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, 
        total=total, css_framework='boostrap5')
    return render_template("home.html", games=games_paginated, username="", 
        page=page, per_page= per_page, pagination=pagination)


# Get Game Description page
@app.route('/games/<id>') 
def game(id):
    game = mongo.db.games.find_one({"_id": ObjectId(id)})
    if game == None:
        return render_template("404.html")
    return render_template("game.html", game=game)


# USER ACCOUNT:

# Register:
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for(
            "profile", username=session["user"]))

    return render_template("index.html", modal='#registerModal')


# Login:
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("{} successfully logged in!".format(
                    request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("index.html", modal='#loginModal')


# Profile:
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        games = mongo.db.games.find(
            {"created_by": username}
        )
        return render_template("profile.html", username=username, games=games)

    return redirect(url_for("login"))


# Logout:
@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect('/')


# Upload Game/Add Game:
@app.route("/upload_game", methods=["GET", "POST"])
def upload_game():
    if request.method == "POST":
        games = {
            "title": request.form.get("title"),
            "photo1": request.form.get("photo1"),
            "photo2": request.form.get("photo2"),
            "link": request.form.get("link"),
            "description": request.form.get("description"),
            "keywords": request.form.get("keywords"),
            "github": request.form.get("github"),
            "linkedin": request.form.get("linkedin"),
            "instagram": request.form.get("instagram"),
            "created_by": session["user"],
            "date": request.form.get("date")
        }
        mongo.db.games.insert_one(games)
        flash("Game Succesfully Added")
        return redirect(url_for("upload_game"))
    return render_template("upload.html")


# Edit Game:
@app.route("/edit/<game_id>", methods=["GET", "POST"])
def edit(game_id):
     if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"]})
        update = {
            "title": request.form.get("title"),
            "photo1": request.form.get("photo1"),
            "photo2": request.form.get("photo2"),
            "link": request.form.get("link"),
            "description": request.form.get("description"),
            "keywords": request.form.get("keywords"),
            "github": request.form.get("github"),
            "linkedin": request.form.get("linkedin"),
            "instagram": request.form.get("instagram"),
            "created_by": session["user"],
            "date": request.form.get("date")
        }              
        mongo.db.games.update({"_id": ObjectId(game_id)}, update)
        flash("Game Updated!")
        return redirect(url_for("profile", username=session["user"]))
             
     game = mongo.db.games.find_one({"_id": ObjectId(game_id)})
     return render_template("edit.html", game=game)


# Delete Game:
@app.route("/delete/<game_id>")
def delete(game_id):
    mongo.db.games.remove({"_id": ObjectId(game_id)})
    flash("Game Successfully Deleted")

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return redirect(url_for("profile", username=username))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
