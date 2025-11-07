# Example 2: Inline Keyboard - Interactive Buttons

**[🇷🇺 Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Creating inline keyboards
- Handling callback queries
- Editing messages
- Button-based navigation

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

### Creating Inline Keyboard

```python
# aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Option 1", callback_data="opt1")],
    [InlineKeyboardButton(text="Option 2", callback_data="opt2")]
])

await message.answer("Choose:", reply_markup=keyboard)

# python-telegram-bot
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Option 1", callback_data="opt1")],
    [InlineKeyboardButton("Option 2", callback_data="opt2")]
])

await update.message.reply_text("Choose:", reply_markup=keyboard)
```

### Handling Callbacks

```python
# aiogram
@router.callback_query(F.data == "opt1")
async def handle_callback(callback: CallbackQuery):
    await callback.answer("You chose Option 1!")
    await callback.message.edit_text("✅ Option 1 selected")

# python-telegram-bot
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer("You chose Option 1!")
    await query.edit_message_text("✅ Option 1 selected")
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for detailed guide on inline keyboards, callback handling, and advanced patterns.

---

**[🇷🇺 Full documentation in Russian](./README_RU.md)**
