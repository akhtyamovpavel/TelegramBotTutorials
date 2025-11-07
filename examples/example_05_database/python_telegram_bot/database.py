import sqlite3
from typing import Optional


class Database:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        """
        Создание таблиц в БД
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    name TEXT,
                    age INTEGER,
                    city TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_user(self, user_id: int, username: Optional[str], full_name: str):
        """
        Добавление пользователя в БД
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username, full_name)
            )
            conn.commit()

    def update_user_profile(self, user_id: int, name: str, age: int, city: str):
        """
        Обновление профиля пользователя
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET name = ?, age = ?, city = ? WHERE user_id = ?",
                (name, age, city, user_id)
            )
            conn.commit()

    def get_user(self, user_id: int):
        """
        Получение данных пользователя
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            return cursor.fetchone()

    def get_all_users_count(self) -> int:
        """
        Получение количества пользователей
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
