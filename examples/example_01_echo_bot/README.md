# Example 1: Echo Bot - The Simplest Bot

**[🇷🇺 Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Basic bot structure
- Command handlers (`/start`, `/help`)
- Message handlers (echo)
- Running bot with polling

## 🚀 Quick Start

### aiogram

```bash
cd aiogram
pip install aiogram==3.13.1
export BOT_TOKEN="your_token_here"
python bot.py
```

### python-telegram-bot

```bash
cd python_telegram_bot
pip install python-telegram-bot==21.7
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

### aiogram

```python
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Hello! I'm an echo bot!")

@router.message(F.text)
async def echo_handler(message: Message):
    await message.answer(message.text)
```

### python-telegram-bot

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def start(update: Update, context):
    await update.message.reply_text("👋 Hello! I'm an echo bot!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

# Register handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for detailed explanations, code comparison, and more examples.

---

**[🇷🇺 Full documentation in Russian](./README_RU.md)**
