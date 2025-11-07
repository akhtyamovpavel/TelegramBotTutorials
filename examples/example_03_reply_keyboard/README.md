# Example 3: Reply Keyboard - Persistent Buttons

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Creating reply keyboards (persistent)
- Requesting location and contact
- Multi-level menus
- Removing keyboards

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

```python
# aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Share Location", request_location=True)],
        [KeyboardButton(text="📱 Share Contact", request_contact=True)]
    ],
    resize_keyboard=True
)

await message.answer("Choose:", reply_markup=keyboard)

# python-telegram-bot
from telegram import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("📍 Share Location", request_location=True)],
    [KeyboardButton("📱 Share Contact", request_contact=True)]
], resize_keyboard=True)

await update.message.reply_text("Choose:", reply_markup=keyboard)
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for detailed guide on reply keyboards and special buttons.

---

**[Full documentation in Russian](./README_RU.md)**
