# Telegram Bot Development with Python

**[Русская версия / Russian version](./README_RU.md)**

A comprehensive educational guide for creating Telegram bots using two popular libraries: **aiogram** and **python-telegram-bot**.

## 📚 Course Content

This repository contains a complete course on Telegram bot development from simple to complex, with examples for both frameworks.

### 🎯 Bot Examples (ordered by complexity)

1. **[Example 1: Echo Bot](./examples/example_01_echo_bot/)** - Simplest bot
   - Basic structure
   - Command and message handlers
   - Running with polling

2. **[Example 2: Inline Keyboard](./examples/example_02_inline_keyboard/)** - Interactive buttons
   - Creating inline keyboards
   - Handling callback queries
   - Editing messages

3. **[Example 3: Reply Keyboard](./examples/example_03_reply_keyboard/)** - Regular buttons
   - ReplyKeyboardMarkup - persistent keyboard
   - Requesting location and contact
   - Multi-level menus

4. **[Example 4: FSM States](./examples/example_04_fsm_states/)** - State machine
   - Multi-step dialogs
   - Storing data between messages
   - User input validation

5. **[Example 5: Database](./examples/example_05_database/)** - Working with databases
   - SQLite integration
   - CRUD operations
   - Middleware (aiogram) / global object (PTB)

6. **[Example 6: Telegram Mini Apps (WebApp)](./examples/example_06_mini_apps/)** - Web applications in Telegram
   - Interactive web interfaces
   - WebAppInfo and WebApp buttons
   - Receiving data via web_app_data
   - Telegram WebApp JavaScript API

7. **[Example 7: File Upload](./examples/example_07_file_upload/)** - File uploads for AI
   - Receiving photos, documents, audio, video
   - Downloading files to server
   - Integration with OCR, Speech-to-Text, NLP

8. **[Example 8: Image Generation](./examples/example_08_image_generation/)** - Image generation
   - Different ways to send images
   - Working with PIL/Pillow
   - Integration with Stable Diffusion, DALL-E, Matplotlib

9. **[Example 9: Media Group Albums](./examples/example_09_media_group_albums/)** - Albums (multiple uploads)
   - Sending albums with multiple images
   - MediaGroupBuilder (aiogram)
   - Handling albums from users
   - Grouping by media_group_id

10. **[Example 10: Telegram Payments](./examples/example_10_telegram_payments/)** - Payments with Telegram Stars
    - Creating invoices for payment
    - Pre-checkout query and successful payment
    - Refunds
    - Monetizing AI features

11. **[Example 11: WebHook Deployment](./examples/example_11_webhook/)** - Production deployment with webhook
    - WebHook instead of polling
    - HTTPS and SSL setup
    - Nginx as reverse proxy
    - Docker deployment
    - VPS, Heroku, Railway, Render

## 🚀 Quick Start

### Requirements

- Python 3.9+
- pip

### Installing Dependencies

Choose one of the frameworks:

```bash
# For aiogram
pip install -r requirements-aiogram.txt

# For python-telegram-bot
pip install -r requirements-ptb.txt

# Or install both
pip install -r requirements.txt
```

### Creating a Bot

1. Find [@BotFather](https://t.me/BotFather) in Telegram
2. Send the command `/newbot`
3. Follow the instructions to get your token
4. Save the token as an environment variable:

```bash
export BOT_TOKEN="your_bot_token_here"
```

### Running an Example

```bash
# aiogram version
python examples/example_01_echo_bot/aiogram/bot.py

# python-telegram-bot version
python examples/example_01_echo_bot/python_telegram_bot/bot.py
```

## 📁 Project Structure

```
TelegramBot/
├── LECTURE.md                          # Main lecture materials
├── README.md                           # This file
├── requirements.txt                    # All dependencies
├── requirements-aiogram.txt            # Only aiogram
├── requirements-ptb.txt                # Only python-telegram-bot
│
└── examples/
    ├── example_01_echo_bot/
    │   ├── README.md                   # Example description
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_02_inline_keyboard/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_03_reply_keyboard/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_04_fsm_states/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_05_database/
    │   ├── README.md
    │   ├── aiogram/
    │   │   ├── bot.py
    │   │   ├── database.py
    │   │   └── users.db (created automatically)
    │   └── python_telegram_bot/
    │       ├── bot.py
    │       ├── database.py
    │       └── users.db (created automatically)
    │
    ├── example_06_mini_apps/
    │   ├── README.md
    │   ├── webapp/
    │   │   └── index.html
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_07_file_upload/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_08_image_generation/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_09_media_group_albums/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    ├── example_10_telegram_payments/
    │   ├── README.md
    │   ├── aiogram/
    │   │   └── bot.py
    │   └── python_telegram_bot/
    │       └── bot.py
    │
    └── example_11_webhook/
        ├── README.md
        ├── aiogram/
        │   └── bot_webhook.py
        └── python_telegram_bot/
            └── bot_webhook.py
```

## 🔗 Useful Links

### aiogram
- [Official Documentation](https://docs.aiogram.dev/)
- [GitHub](https://github.com/aiogram/aiogram)
- [Community Chat](https://t.me/aiogram)

### python-telegram-bot
- [Official Documentation](https://docs.python-telegram-bot.org/)
- [GitHub](https://github.com/python-telegram-bot/python-telegram-bot)
- [Wiki with Examples](https://github.com/python-telegram-bot/python-telegram-bot/wiki)

### Telegram Bot API
- [Official API Documentation](https://core.telegram.org/bots/api)
- [BotFather](https://t.me/BotFather) - create bots
- [Telegram Bots Guide](https://core.telegram.org/bots)

## 💡 Advanced Topics

After learning the basics, we recommend exploring:

1. **Webhook** instead of polling
2. **Docker** for deployment
3. **Redis** for state storage
4. **PostgreSQL** for production databases
5. **Logging and monitoring**
6. **Bot testing**
7. **CI/CD** pipeline
8. **Paid Media** - paid content (images, video)
9. **Inline mode** - inline queries
10. **Bot API Server** - self-hosted Bot API server
11. **Webhook** - webhook for deployment

## 🤝 Contributing

If you found an error or want to improve the material:

1. Create an Issue describing the problem
2. Suggest a Pull Request with fixes
3. Share your ideas

## 📝 License

This educational material is provided "as is" for free use in educational purposes.

## ✨ Authors

This educational guide was developed for students of HSE University, AI program.

---

**Good luck learning Telegram bot development!** 🚀🤖
