# Example 9: Media Group Albums - Multiple Images

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Sending albums (multiple images)
- MediaGroupBuilder (aiogram)
- Receiving albums from users
- Grouping by media_group_id

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

```python
# aiogram - Send album
from aiogram.types import FSInputFile, InputMediaPhoto

media_group = [
    InputMediaPhoto(media=FSInputFile("image1.jpg"), caption="Photo 1"),
    InputMediaPhoto(media=FSInputFile("image2.jpg"), caption="Photo 2"),
    InputMediaPhoto(media=FSInputFile("image3.jpg"), caption="Photo 3")
]

await message.answer_media_group(media_group)

# python-telegram-bot - Send album
from telegram import InputMediaPhoto

media = [
    InputMediaPhoto(open("image1.jpg", "rb"), caption="Photo 1"),
    InputMediaPhoto(open("image2.jpg", "rb"), caption="Photo 2"),
    InputMediaPhoto(open("image3.jpg", "rb"), caption="Photo 3")
]

await update.message.reply_media_group(media)
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for complete media groups guide.

---

**[Full documentation in Russian](./README_RU.md)**
