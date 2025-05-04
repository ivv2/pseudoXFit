import sqlite3

# ---- DATABASE CONNECTION ----
def get_db(dbfile):
    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row
    return conn

# ---- DATABASE INIT ----
def init_db(dbfile, fitness_mode=False):
    conn = get_db(dbfile)
    c = conn.cursor()
    if not fitness_mode:
        # PSEUDO GAME DB SETUP (playgame.db)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                experience INTEGER NOT NULL DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                health INTEGER,
                battle_points INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
    else:
        # FITNESS TRACKER DB SETUP (fitnesstracker.db)
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL
        );""")
        c.execute("""CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        );""")
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

# ===========================
# ===== PSEUDO GAME =====
# ===========================

# ---- user (game) ----
def add_game_user(username, password):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def get_game_user(username):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_game_user_by_id(user_id):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_experience(user_id, gained_exp):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("UPDATE users SET experience = experience + ? WHERE id = ?", (gained_exp, user_id))
    conn.commit()
    conn.close()

def update_user_level(user_id, new_level):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
    conn.commit()
    conn.close()

def add_game(user_id, health, battle_points):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("INSERT INTO games (user_id, health, battle_points) VALUES (?, ?, ?)", (user_id, health, battle_points))
    conn.commit()
    conn.close()

def get_user_games(user_id):
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("SELECT * FROM games WHERE user_id = ?", (user_id,))
    games = c.fetchall()
    conn.close()
    return games

def get_ranga_tabula():
    conn = get_db("playgame.db")
    c = conn.cursor()
    c.execute("""
        SELECT users.username, users.level, users.experience, COUNT(games.id) as game_count
        FROM users
        LEFT JOIN games ON users.id = games.user_id
        GROUP BY users.id
        ORDER BY game_count DESC
    """)
    ranga = c.fetchall()
    conn.close()
    return ranga

# ===========================
# ===== FITNESS TRACKER =====
# ===========================

# -------- users
def add_fit_user(name, surname):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (name, surname) VALUES (?, ?)", (name, surname))
    conn.commit()
    conn.close()

def get_all_fit_users():
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY surname ASC, name ASC")
    users = c.fetchall()
    conn.close()
    return users

# -------- sports
def add_sport(title):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("INSERT INTO sports (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

def get_all_sports():
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sports ORDER BY title ASC")
    sports = c.fetchall()
    conn.close()
    return sports

# -------- workouts
def add_workout(user_id, sport_id, intensity, day_time):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("""INSERT INTO workouts (user_id, sport_id, intensity, day_time)
                 VALUES (?, ?, ?, ?)""", (user_id, sport_id, intensity, day_time))
    conn.commit()
    conn.close()

def get_all_workouts():
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("""SELECT w.id, u.name, u.surname, s.title as sport, w.intensity, w.day_time
                 FROM workouts w
                 JOIN users u ON w.user_id = u.id
                 JOIN sports s ON w.sport_id = s.id
                 ORDER BY w.id DESC""")
    workouts = c.fetchall()
    conn.close()
    return workouts

def get_user_workouts(user_id):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("SELECT * FROM workouts WHERE user_id=?", (user_id,))
    items = c.fetchall()
    conn.close()
    return items

def get_user_stats(user_id):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    # Favourite sport (sport w most workouts)
    c.execute("""SELECT sport_id, COUNT(*) as cnt
                 FROM workouts WHERE user_id=?
                 GROUP BY sport_id ORDER BY cnt DESC LIMIT 1""", (user_id,))
    row = c.fetchone()
    fav_sport_id = row["sport_id"] if row else None

    c.execute("SELECT AVG(intensity) as avg_i FROM workouts WHERE user_id=?", (user_id,))
    avg_i_row = c.fetchone()
    avg_intensity = round(avg_i_row["avg_i"], 2) if avg_i_row and avg_i_row["avg_i"] else None

    c.execute("""SELECT day_time, COUNT(*) as cnt FROM workouts WHERE user_id=?
                 GROUP BY day_time ORDER BY cnt DESC LIMIT 1""", (user_id,))
    time_row = c.fetchone()
    fav_day_time = time_row["day_time"] if time_row else None

    fav_sport_name = None
    if fav_sport_id:
        c.execute("SELECT title FROM sports WHERE id=?", (fav_sport_id,))
        sport_row = c.fetchone()
        if sport_row:
            fav_sport_name = sport_row['title']
    conn.close()
    return fav_sport_name, avg_intensity, fav_day_time

def delete_workout(workout_id):
    conn = get_db("fitnesstracker.db")
    c = conn.cursor()
    c.execute("DELETE FROM workouts WHERE id=?", (workout_id,))
    conn.commit()
    conn.close()