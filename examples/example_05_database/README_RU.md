# Example 5: Работа с базой данных

## Описание

Бот с полноценной базой данных:
- Регистрирует пользователей при `/start`
- Сохраняет профиль после завершения регистрации
- Позволяет просматривать профиль `/profile`
- Показывает статистику пользователей `/stats`

## Что нового по сравнению с Example 3

### ➕ Добавлено:
1. **database.py** - модуль для работы с SQLite
2. **CRUD операции** - Create, Read, Update для пользователей
3. **Middleware (aiogram)** - автоматическая передача объекта БД
4. **Асинхронная БД (aiogram)** - использование `aiosqlite`
5. **Новые команды** - `/profile`, `/stats`

### Что изменилось:
- Данные теперь **сохраняются** между запусками бота
- Добавлена логика работы с базой данных
- В aiogram используется middleware для dependency injection
- В python-telegram-bot - глобальный объект БД

## Структура файлов

```
example_04_database/
├── aiogram/
│   ├── bot.py          # Основной файл бота
│   ├── database.py     # Работа с БД
│   └── users.db        # SQLite база (создается автоматически)
└── python_telegram_bot/
    ├── bot.py
    ├── database.py
    └── users.db
```

## Установка

```bash
# Для aiogram (требуется aiosqlite)
pip install aiogram aiosqlite

# Для python-telegram-bot (sqlite3 входит в стандартную библиотеку)
pip install python-telegram-bot
```

## Запуск

```bash
export BOT_TOKEN="your_bot_token_here"

# aiogram
python examples/example_04_database/aiogram/bot.py

# python-telegram-bot
python examples/example_04_database/python_telegram_bot/bot.py
```

## Ключевые концепции

### База данных SQLite
SQLite - легковесная встраиваемая БД, идеальна для начала:
- Не требует отдельного сервера
- Хранится в одном файле
- Поддерживает SQL запросы

### Структура таблицы users

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,      -- Telegram ID
    username TEXT,                     -- @username
    full_name TEXT,                    -- Полное имя
    name TEXT,                         -- Имя из анкеты
    age INTEGER,                       -- Возраст
    city TEXT,                         -- Город
    created_at TIMESTAMP               -- Дата регистрации
)
```

### Middleware (aiogram)

**Что это?**
Middleware - промежуточный слой, который выполняется **перед** обработчиком.

**Зачем?**
- Передать объект БД в каждый обработчик автоматически
- Избежать глобальных переменных
- Dependency Injection pattern

```python
class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database

    async def __call__(self, handler, event, data):
        data["db"] = self.database  # Добавляем БД в контекст
        return await handler(event, data)
```

Теперь в любом обработчике:
```python
async def my_handler(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
```

### Асинхронная vs Синхронная БД

**aiogram (aiosqlite):**
```python
async with aiosqlite.connect(self.db_path) as db:
    await db.execute("SELECT * FROM users")
```

**python-telegram-bot (sqlite3):**
```python
with sqlite3.connect(self.db_path) as conn:
    conn.execute("SELECT * FROM users")
```

## CRUD операции

### Create - Создание пользователя
```python
await db.add_user(user_id, username, full_name)
```

### Read - Чтение данных
```python
user = await db.get_user(user_id)
count = await db.get_all_users_count()
```

### Update - Обновление профиля
```python
await db.update_user_profile(user_id, name, age, city)
```

### Delete - Удаление (не реализовано в примере)
```python
await db.delete_user(user_id)
```

## Сравнение подходов

| Аспект | aiogram | python-telegram-bot |
|--------|---------|---------------------|
| **Библиотека БД** | `aiosqlite` (async) | `sqlite3` (sync) |
| **Передача БД** | Middleware + DI | Глобальный объект |
| **Операции** | `await db.method()` | `db.method()` |
| **Контекст** | `async with connect()` | `with connect()` |
| **Параметр функции** | `db: Database` | Не требуется |

## Важные моменты

### Инициализация БД

**aiogram:**
```python
db = Database()
await db.create_tables()  # Асинхронно!
```

**python-telegram-bot:**
```python
db = Database()  # Таблицы создаются в __init__
```

### SQL Injection защита

✅ **Правильно** (используем параметры):
```python
cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
```

❌ **Неправильно** (уязвимо):
```python
cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
```

### Row Factory

Для удобства работы с результатами:
```python
db.row_factory = sqlite3.Row  # Доступ по имени: row['name']
```

## Дальнейшие улучшения

1. **Миграции** - использовать Alembic для версионирования схемы
2. **ORM** - SQLAlchemy (async), Tortoise ORM
3. **PostgreSQL** - для production вместо SQLite
4. **Пул соединений** - для оптимизации
5. **Индексы** - для ускорения запросов
6. **Транзакции** - для атомарных операций

## Production рекомендации

### Для aiogram:
- Используйте PostgreSQL с asyncpg
- Или SQLAlchemy (async mode)
- RedisStorage для FSM состояний

### Для python-telegram-bot:
- Используйте PostgreSQL с psycopg2
- Или SQLAlchemy (sync mode)
- Пул соединений для оптимизации

### Общие советы:
- Храните токен в переменных окружения
- Используйте логирование
- Обрабатывайте ошибки БД
- Делайте резервные копии
- Мониторьте производительность
