from flask import Flask, render_template, request, redirect, url_for, flash
import os
import models

app = Flask(__name__)
app.secret_key = "fitnesa_secret"

# Init DB if not exists
if not os.path.exists("fitnesstracker.db"):
    models.init_db()

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Add new user
@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        name = request.form["name"].strip()
        surname = request.form["surname"].strip()
        if name and surname:
            models.add_user(name, surname)
            flash("Lietotājs pievienots!")
        else:
            flash("Aizpildi visus laukus!")
        return redirect(url_for("index"))
    return render_template("new_user.html")

# Add new sport
@app.route("/new_sport", methods=["GET", "POST"])
def new_sport():
    if request.method == "POST":
        title = request.form["title"].strip()
        if title:
            models.add_sport(title)
            flash("Sporta veids pievienots!")
        else:
            flash("Ievadi sporta veida nosaukumu!")
        return redirect(url_for("index"))
    return render_template("new_sport.html")

# Add new workout
@app.route("/new_workout", methods=["GET", "POST"])
def new_workout():
    users = models.get_all_users()
    sports = models.get_all_sports()
    if request.method == "POST":
        user_id = request.form["user_id"]
        sport_id = request.form["sport_id"]
        intensity = request.form["intensity"]
        day_time = request.form["day_time"]
        if user_id and sport_id and intensity and day_time:
            models.add_workout(user_id, sport_id, intensity, day_time)
            # Print & log to file as required (Part 6, step 5)
            print(f"Treniņš: Lietotājs {user_id}, Sports {sport_id}, Intensitāte {intensity}, Laiks {day_time}")
            with open("kontrole.txt", "a", encoding="utf-8") as f:
                f.write(f"Lietotājs {user_id}, Sports {sport_id}, Intensitāte {intensity}, Laiks {day_time}\n")
            flash("Treniņš pievienots!")
        else:
            flash("Aizpildi visus laukus!")
        return redirect(url_for("index"))
    return render_template("new_workout.html", users=users, sports=sports)

# List all sports (sorted)
@app.route("/sports")
def sports_list():
    sports = models.get_all_sports()
    return render_template("sports_list.html", sports=sports)

# List all workouts
@app.route("/workouts")
def workouts_list():
    workouts = models.get_all_workouts()
    return render_template("workouts_list.html", workouts=workouts)

# List all users, with stats
@app.route("/users")
def users_list():
    users = models.get_all_users()
    # Get stats for each user
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
    return render_template("users_list.html", userstats=userstats)

# Confirm delete workout
@app.route("/delete_workout/<int:workout_id>", methods=["GET", "POST"])
def delete_workout_confirm(workout_id):
    if request.method == "POST":
        models.delete_workout(workout_id)
        flash("Treniņš dzēsts!")
        return redirect(url_for("workouts_list"))
    return render_template("delete_workout_confirm.html", workout_id=workout_id)

# for local debug
#if __name__ == "__main__":
#    app.run(debug=True)