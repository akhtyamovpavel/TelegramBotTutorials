# Example 1: Простой Echo Bot

## Описание

Простейший бот, который:
- Отвечает на команду `/start` приветствием
- Повторяет все текстовые сообщения пользователя

## Что изучаем

1. **Основы структуры бота**
2. **Асинхронные функции** (`async`/`await`)
3. **Регистрация обработчиков** команд и сообщений
4. **Запуск polling** (получение обновлений от Telegram)

## Установка

```bash
# Для aiogram
pip install aiogram

# Для python-telegram-bot
pip install python-telegram-bot
```

## Запуск

```bash
# Установите токен бота
export BOT_TOKEN="your_bot_token_here"

# Запустите aiogram версию
python examples/example_01_echo_bot/aiogram/bot.py

# Или python-telegram-bot версию
python examples/example_01_echo_bot/python_telegram_bot/bot.py
```

## Ключевые различия между библиотеками

### aiogram
- Использует `Router` для организации обработчиков
- Magic Filter `F.text` для фильтрации
- Декораторы `@router.message(...)`
- `message.answer()` для ответа

### python-telegram-bot
- Использует `Application` и `add_handler()`
- Модуль `filters.TEXT` для фильтрации
- Явная регистрация через `CommandHandler`, `MessageHandler`
- `update.message.reply_text()` для ответа
