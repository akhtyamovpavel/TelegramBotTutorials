# Example 7: File Upload - Handling Media for AI

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Receiving photos, documents, audio, video
- Downloading files to server
- File processing
- Integration with OCR, Speech-to-Text, NLP

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
@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    # Get largest photo
    photo = message.photo[-1]

    # Download file
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path

    await bot.download_file(file_path, "photo.jpg")

    await message.answer("✅ Photo received and saved!")

# python-telegram-bot
async def photo_handler(update: Update, context):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("photo.jpg")

    await update.message.reply_text("✅ Photo received!")
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for complete file handling guide.

---

**[Full documentation in Russian](./README_RU.md)**
