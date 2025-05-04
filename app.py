from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import random

import models  # Your combined models.py (see below)

app = Flask(__name__)
app.secret_key = "fitnesa_secret_change_this"

# --- DB INITS ---
# Ensure both DBs exist, or combine into one if you wish
if not os.path.exists("playgame.db"):
    models.init_db("playgame.db")
if not os.path.exists("fitnesstracker.db"):
    models.init_db("fitnesstracker.db", fitness_mode=True)

# --- PSEUDO GAME (default homepage) ---
with open("texts.json", encoding="utf-8") as f:
    TEXTS = json.load(f)

with open("level_requirements.json") as f:
    LEVELS = {int(k): v for k,v in json.load(f).items()}

def get_level_and_next_exp(experience):
    level = 1
    for lvl, need_exp in sorted(LEVELS.items()):
        if experience >= need_exp:
            level = lvl + 1
        else:
            break
    req = LEVELS.get(level, None)
    return level, req - experience if req else None

@app.route("/")
def index():
    return render_template("index.html", TEXTS=TEXTS)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if models.get_game_user(username):
            flash("Username taken!")
            return redirect(url_for("register"))
        models.add_game_user(username, password)
        flash("Registered! Please login.")
        return redirect(url_for("login"))
    return render_template("register.html", TEXTS=TEXTS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = models.get_game_user(username)
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed!")
    return render_template("login.html", TEXTS=TEXTS)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = None
    exp_needed = 0
    games_count = 0
    if "user_id" in session:
        user_row = models.get_game_user_by_id(session["user_id"])
        level, next_exp = get_level_and_next_exp(user_row["experience"])
        games = models.get_user_games(session['user_id'])
        games_count = len(games)
        exp_needed = next_exp
        user = dict(user_row)
        user["level"] = level
        user["exp_needed"] = exp_needed
        user["games_count"] = games_count
    return render_template("dashboard.html", TEXTS=TEXTS, user=user)

@app.route("/start_game", methods=["GET"])
def start_game():
    if "user_id" not in session:
        flash("Please login")
        return redirect(url_for("login"))
    session["game"] = {"health": 100, "battle_points": 0}
    return render_template("game.html", TEXTS=TEXTS, health=100, battle_points=0)

@app.route("/play", methods=["POST"])
def play():
    if "game" not in session or "user_id" not in session:
        flash("Please start a new game.")
        return redirect(url_for("dashboard"))
    game = session["game"]
    action = request.form["action"]
    if action == "fight":
        loss = random.randint(12, 26)
        gain = random.randint(10, 30)
        game["health"] -= loss
        game["battle_points"] += gain
        if game["health"] <= 0:
            models.add_game(session["user_id"], 0, game["battle_points"])
            models.update_user_experience(session["user_id"], game["battle_points"])
            session.pop("game")
            flash(TEXTS["game_over"])
            return redirect(url_for("dashboard"))
        else:
            session["game"] = game
            return render_template("game.html", TEXTS=TEXTS, health=game["health"], battle_points=game["battle_points"])
    elif action == "run":
        models.add_game(session["user_id"], game["health"], game["battle_points"])
        models.update_user_experience(session["user_id"], game["battle_points"])
        session.pop("game")
        flash(TEXTS["game_over"])
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid action")
        return redirect(url_for("dashboard"))

@app.route("/my_games")
def my_games():
    if "user_id" not in session:
        flash("Please login!")
        return redirect(url_for("login"))
    games = models.get_user_games(session["user_id"])
    return render_template("games_list.html", TEXTS=TEXTS, games=games)

# --- FITNESS TRACKER SECTION ---
@app.route("/majasdarbi/fitnesstracker/")
def fitnesstracker_main():
    return render_template("fitnesstracker/fit_menu.html")

@app.route("/majasdarbi/fitnesstracker/new_user", methods=["GET", "POST"])
def fit_new_user():
    if request.method == "POST":
        name = request.form["name"].strip()
        surname = request.form["surname"].strip()
        if name and surname:
            models.add_fit_user(name, surname)
            flash("Lietotājs pievienots!")
        else:
            flash("Aizpildi visus laukus!")
        return redirect(url_for("fitnesstracker_main"))
    return render_template("fitnesstracker/new_user.html")

@app.route("/majasdarbi/fitnesstracker/new_sport", methods=["GET", "POST"])
def fit_new_sport():
    if request.method == "POST":
        title = request.form["title"].strip()
        if title:
            models.add_sport(title)
            flash("Sporta veids pievienots!")
        else:
            flash("Ievadi sporta veida nosaukumu!")
        return redirect(url_for("fitnesstracker_main"))
    return render_template("fitnesstracker/new_sport.html")

@app.route("/majasdarbi/fitnesstracker/new_workout", methods=["GET", "POST"])
def fit_new_workout():
    users = models.get_all_fit_users()
    sports = models.get_all_sports()
    if request.method == "POST":
        user_id = request.form["user_id"]
        sport_id = request.form["sport_id"]
        intensity = request.form["intensity"]
        day_time = request.form["day_time"]
        if user_id and sport_id and intensity and day_time:
            models.add_workout(user_id, sport_id, intensity, day_time)
            print(f"Treniņš: Lietotājs {user_id}, Sports {sport_id}, Intensitāte {intensity}, Laiks {day_time}")
            with open("kontrole.txt", "a", encoding="utf-8") as f:
                f.write(f"Lietotājs {user_id}, Sports {sport_id}, Intensitāte {intensity}, Laiks {day_time}\n")
            flash("Treniņš pievienots!")
        else:
            flash("Aizpildi visus laukus!")
        return redirect(url_for("fitnesstracker_main"))
    return render_template("fitnesstracker/new_workout.html", users=users, sports=sports)

@app.route("/majasdarbi/fitnesstracker/sports")
def fit_sports_list():
    sports = models.get_all_sports()
    return render_template("fitnesstracker/sports_list.html", sports=sports)

@app.route("/majasdarbi/fitnesstracker/workouts")
def fit_workouts_list():
    workouts = models.get_all_workouts()
    return render_template("fitnesstracker/workouts_list.html", workouts=workouts)

@app.route("/majasdarbi/fitnesstracker/users")
def fit_users_list():
    users = models.get_all_fit_users()
    userstats = []
    for user in users:
        fav_sport, avg_intensity, fav_time = models.get_user_stats(user["id"])
        userstats.append({
            "name": user["name"],
            "surname": user["surname"],
            "fav_sport": fav_sport,
            "avg_intensity": avg_intensity,
            "fav_time": fav_time
        })
    return render_template("fitnesstracker/users_list.html", userstats=userstats)

@app.route("/majasdarbi/fitnesstracker/delete_workout/<int:workout_id>", methods=["GET", "POST"])
def fit_delete_workout_confirm(workout_id):
    if request.method == "POST":
        models.delete_workout(work)