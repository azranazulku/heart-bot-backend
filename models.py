import sqlite3
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DB:
    def __init__(self, db_path="users.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_users_table()

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            birth_date TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def create_user(self, first_name, last_name, username, birth_date, email, password):
        password_hash = self.hash_password(password)
        created_at = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, username, birth_date, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, username, birth_date, email, password_hash, created_at)
        )
        self.conn.commit()
        user_id = cursor.lastrowid
        return self.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
