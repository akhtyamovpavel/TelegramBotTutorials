import aiosqlite
from typing import Optional


class Database:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path

    async def create_tables(self):
        """
        Создание таблиц в БД
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
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
            await db.commit()

    async def add_user(self, user_id: int, username: Optional[str], full_name: str):
        """
        Добавление пользователя в БД
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username, full_name)
            )
            await db.commit()

    async def update_user_profile(self, user_id: int, name: str, age: int, city: str):
        """
        Обновление профиля пользователя
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET name = ?, age = ?, city = ? WHERE user_id = ?",
                (name, age, city, user_id)
            )
            await db.commit()

    async def get_user(self, user_id: int):
        """
        Получение данных пользователя
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone()

    async def get_all_users_count(self) -> int:
        """
        Получение количества пользователей
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                result = await cursor.fetchone()
                return result[0]
