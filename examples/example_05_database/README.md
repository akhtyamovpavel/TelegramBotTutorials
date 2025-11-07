# Example 5: Database Integration - SQLite

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- SQLite database integration
- CRUD operations (Create, Read, Update, Delete)
- User data persistence
- Middleware/context managers

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

```python
import sqlite3

# Create database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_seen TIMESTAMP,
            message_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Save user
def save_user(user_id, username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_seen, message_count)
        VALUES (?, ?, datetime('now'), 1)
    ''', (user_id, username))
    conn.commit()
    conn.close()
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for complete database guide with examples.

---

**[Full documentation in Russian](./README_RU.md)**
