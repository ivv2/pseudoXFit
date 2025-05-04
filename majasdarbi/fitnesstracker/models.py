import sqlite3

DB = "fitnesstracker.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL
    );""")
    # Sports table
    c.execute("""CREATE TABLE IF NOT EXISTS sports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
    );""")
    # Workouts table
    c.execute("""CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sport_id INTEGER NOT NULL,
        intensity INTEGER NOT NULL,
        day_time TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(sport_id) REFERENCES sports(id)
    );""")
    conn.commit()
    conn.close()

# Add user
def add_user(name, surname):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO users (name, surname) VALUES (?, ?)", (name, surname))
    conn.commit()
    conn.close()

# Add sport
def add_sport(title):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO sports (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

# Add workout
def add_workout(user_id, sport_id, intensity, day_time):
    conn = get_db()
    c = conn.cursor()
    c.execute("""INSERT INTO workouts (user_id, sport_id, intensity, day_time)
                 VALUES (?, ?, ?, ?)""", (user_id, sport_id, intensity, day_time))
    conn.commit()
    conn.close()

# Get all users (alphabetical order by surname)
def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY surname ASC, name ASC")
    users = c.fetchall()
    conn.close()
    return users

# Get all sports (alphabetical order)
def get_all_sports():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sports ORDER BY title ASC")
    sports = c.fetchall()
    conn.close()
    return sports

# Get all workouts, joined
def get_all_workouts():
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT w.id, u.name, u.surname, s.title as sport, w.intensity, w.day_time
                 FROM workouts w
                 JOIN users u ON w.user_id = u.id
                 JOIN sports s ON w.sport_id = s.id
                 ORDER BY w.id DESC""")
    workouts = c.fetchall()
    conn.close()
    return workouts

# Get all workouts for a user
def get_user_workouts(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM workouts WHERE user_id=?", (user_id,))
    items = c.fetchall()
    conn.close()
    return items

# For stats: most popular sport, avg intensity, fav time
def get_user_stats(user_id):
    conn = get_db()
    c = conn.cursor()
    # Favourite sport (sport w most workouts)
    c.execute("""SELECT sport_id, COUNT(*) as cnt 
                 FROM workouts WHERE user_id=?
                 GROUP BY sport_id ORDER BY cnt DESC LIMIT 1""", (user_id,))
    row = c.fetchone()
    fav_sport_id = row["sport_id"] if row else None
    
    # Avg intensity
    c.execute("SELECT AVG(intensity) as avg_i FROM workouts WHERE user_id=?", (user_id,))
    avg_i_row = c.fetchone()
    avg_intensity = round(avg_i_row["avg_i"], 2) if avg_i_row and avg_i_row["avg_i"] else None
    
    # Fav day_time ("Rīta treniņš" or "Vakara treniņš")
    c.execute("""SELECT day_time, COUNT(*) as cnt FROM workouts WHERE user_id=?
                 GROUP BY day_time ORDER BY cnt DESC LIMIT 1""", (user_id,))
    time_row = c.fetchone()
    fav_day_time = time_row["day_time"] if time_row else None
    
    # Sport name for fav sport
    fav_sport_name = None
    if fav_sport_id:
        c.execute("SELECT title FROM sports WHERE id=?", (fav_sport_id,))
        sport_row = c.fetchone()
        if sport_row:
            fav_sport_name = sport_row['title']
    conn.close()
    return fav_sport_name, avg_intensity, fav_day_time

# Get user by id
def get_user_by_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    item = c.fetchone()
    conn.close()
    return item

# Get sport by id
def get_sport_by_id(sport_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sports WHERE id=?", (sport_id,))
    item = c.fetchone()
    conn.close()
    return item

# Delete workout by id
def delete_workout(workout_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM workouts WHERE id=?", (workout_id,))
    conn.commit()
    conn.close()