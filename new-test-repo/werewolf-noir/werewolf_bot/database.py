import sqlite3
import os

DB_PATH = 'werewolf.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 450,
            favorite_role TEXT DEFAULT 'Обыватель',
            rating INTEGER DEFAULT 1000,
            next_role TEXT DEFAULT NULL
        )''')
        conn.commit()

def get_user(user_id, username="Unknown"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
        
        return {
            "user_id": user[0], "username": user[1], "wins": user[2],
            "losses": user[3], "coins": user[4], "favorite_role": user[5],
            "rating": user[6], "next_role": user[7]
        }

def update_user_coins(user_id, amount):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

def update_user_stats(user_id, is_win):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if is_win:
            cursor.execute("UPDATE users SET wins = wins + 1, coins = coins + 50, rating = rating + 25 WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("UPDATE users SET losses = losses + 1, rating = rating - 15 WHERE user_id = ?", (user_id,))
        conn.commit()

def set_next_role(user_id, role):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET next_role = ? WHERE user_id = ?", (role, user_id))
        conn.commit()
